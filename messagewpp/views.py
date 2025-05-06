#Nunca mas te metas a un Framework sin conocer el lenguaje xd 
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import os , requests, re, json , logging, io, datetime, base64
import google.generativeai as genai
from django.shortcuts import render, redirect, get_object_or_404
from twilio.rest import Client
from django.http import JsonResponse, HttpResponse
from .forms import SendForm, CreateNewMessageTemplate, UploadFileForm
from .models import MessageTemplate, UploadedFile, WhatsappUser, PlaceTrigal
from session.models import MessageAI
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from io import BytesIO
from django.http import HttpResponse
import matplotlib.pyplot as plt
import tempfile
from pdf2image import convert_from_path
from datetime import datetime
from PIL import Image
from docx2pdf import convert

def MessagingAI(UserInput):

    genai.configure(api_key=settings.API_KEY_GEMINI)  

    model = genai.GenerativeModel('gemini-2.0-flash')

    role = "Eres un asistente que responde basado en un listado de preguntas y respuestas. Si la pregunta no coincide con ninguna del listado, di: 'Para una pregunta detallada, un asesor te contactará (horario: 6:00 am - 2:30 pm)'."

    MessageList = MessageAI.objects.all().values_list('ask', 'answer')
    formatted_list = "\n" .join(f"Pregunta: {ask} \nRepuesta: {answer}" for ask, answer in MessageList)

    context = f"Listado de preguntas/respuestas:\n{formatted_list}\n\nUsuario pregunta: {UserInput}"
    
    try:
        response = model.generate_content({
            "role": "user",
            "parts": [f"{role}\n\n{context}"]
        })
        return response.text
    except Exception as e:
        print(e)
        return f"Para una pregunta detallada, un asesor te contactará"


logger = logging.getLogger(__name__)



def ai_validate_file_function(mediaUrl, mediaType, id_user_file):

    """
    Valida si un archivo PDF es una hoja de vida usando Google Generative AI.
    Extrae el texto del PDF y lo pasa a Gemini para su análisis.
    Si el PDF es una imagen, usa OCR para extraer el texto.
    Devuelve True si es una hoja de vida, False si no lo es.
    """
    genai.configure(api_key=settings.API_KEY_GEMINI)
    model = genai.GenerativeModel('gemini-2.0-flash')  

    info_user_with_ia = WhatsappUser.objects.get(id=id_user_file)
    auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN) # Creedenciales para Twilio
    response = requests.get(mediaUrl, auth=auth) 
    temp_file_path = None
    response.raise_for_status()  # Verificar si la descarga fue exitosa
    file_content = BytesIO(response.content)
    try:

        role = (
                "Eres un asistente que analiza el contenido de un archivo para determinar si es una hoja de vida. "
                "Si el archivo contiene información personal como nombre, experiencia laboral, educación o habilidades, "
                "devuelve únicamente un objeto JSON crudo, sin ningún texto adicional, sin etiquetas de Markdown como ```json o ```, "
                "sin espacios ni líneas extras, con las claves: 'Nombre Completo', 'Documento', 'Experiencia', 'Direccion Domiciliaria' "
                "El valor de la clave 'Documento' debe ir sin puntos, comas, guiones o cualquier caracter especial. Unicamente numeros"
                "Si alguno de estos datos no se encuentra, su valor será 'Dato no encontrado -IA'. "
                "Si NO es una hoja de vida o no se puede extraer información, responde únicamente con la palabra 'False' (sin comillas, como texto plano). "
                "IMPORTANTE: No uses Markdown, no envuelvas la respuesta en ```json ni en ningún otro formato."
            )
        
        context = [role]


        # Generar respuesta con Gemini
        if mediaType == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
            with tempfile.NamedTemporaryFile(delete=False, suffix='.docx') as temp_file_word:
                temp_file_word.write(file_content.getvalue())
                temp_file_word_path = temp_file_word.name

            temp_pdf_path = os.path.splitext(temp_file_word_path)[0] + ".pdf"

            convert(temp_file_word_path, temp_pdf_path)

            images = convert_from_path(temp_pdf_path, dpi=300, poppler_path=r"C:\poppler-24.08.0\Library\bin")
            
            for i, img in enumerate(images):
                logger.info(f"imagen # {i}")
                logger.info(f"Se convirtieron {len(images)} páginas del PDF a imágenes.")
                context.append(img)

            response = model.generate_content(context)
            response_text = response.text.strip()
            print(type(response_text))
            print(response_text)

            if response_text != 'False':
                try:
                    datos = json.loads(response_text)
                except json.JSONDecodeError as e:
                    return f"Hubo un problema al parsear el JSON {e}"
                except Exception as e:
                    logger.error(f"Ocurrió un error inesperado al procesar el JSON: {e}")
                    return False

                try:
                    info_user_with_ia.nameUser = datos["Nombre Completo"]
                    info_user_with_ia.documentUser = datos["Documento"]
                    info_user_with_ia.experienceUser = datos["Experiencia"]
                    info_user_with_ia.placeUser = datos["Direccion Domiciliaria"]
                    info_user_with_ia.save()
                    print("Datos guardados en info_user_with_ia:", info_user_with_ia.nameUser, info_user_with_ia.documentUser, info_user_with_ia.experienceUser, info_user_with_ia.placeUser)
                    return True
                except Exception as e:
                    logger.error(f"Error al guardar los datos del usuario: {e}")
                    return False
                finally: 
                    if temp_pdf_path and os.path.exists(temp_pdf_path):
                        try:
                            os.remove(temp_pdf_path)
                            logger.info(f"Archivo temporal {temp_pdf_path} eliminado.")
                        except OSError as e:
                            logger.warning(f"No se pudo eliminar el archivo temporal {temp_pdf_path}: {e}")
            else:
                return False

        elif mediaType == "application/pdf" :
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                temp_file.write(file_content.getvalue())
                temp_file_path = temp_file.name

            images = convert_from_path(temp_file_path, dpi=300, poppler_path=r"C:\poppler-24.08.0\Library\bin")
            logger.info(f"Se convirtieron {len(images)} páginas del PDF a imágenes.")

            for i, img in enumerate(images):
                logger.info(f'Esta es la imagen {i+1}')
                context.append(img)

            print('response dato:' + str(response.text))
            print('response:' + str(type(response.text)))
            response = model.generate_content(context)
            response_text = response.text.strip()
            print("este es el Json" + response_text)
            if response_text != 'False':
                try:
                    datos = json.loads(response_text)
                except json.JSONDecodeError as e:
                    return f"Hubo un problema al parsear el JSON {e}"
                except Exception as e:
                    logger.error(f"Ocurrió un error inesperado al procesar el JSON: {e}")
                    return False

                try:
                    info_user_with_ia.nameUser = datos["Nombre Completo"]
                    info_user_with_ia.documentUser = datos["Documento"]
                    info_user_with_ia.experienceUser = datos["Experiencia"]
                    info_user_with_ia.placeUser = datos["Direccion Domiciliaria"]
                    info_user_with_ia.save()
                    print("Datos guardados en info_user_with_ia:", info_user_with_ia.nameUser, info_user_with_ia.documentUser, info_user_with_ia.experienceUser, info_user_with_ia.placeUser)
                    return True
                except Exception as e:
                    logger.error(f"Error al guardar los datos del usuario: {e}")
                    return False
                finally: 
                    if temp_file_path and os.path.exists(temp_file_path):
                        try:
                            os.remove(temp_file_path)
                            logger.info(f"Archivo temporal {temp_file_path} eliminado.")
                        except OSError as e:
                            logger.warning(f"No se pudo eliminar el archivo temporal {temp_file_path}: {e}")
            else:
                return False
             
        elif mediaType.startswith("image/"):
            with Image.open(file_content) as Imagen:
                image_format = Imagen.format if Imagen.format in ['JPEG', 'PNG'] else 'JPEG'
                suffix = '.jpg' if image_format == 'JPEG' else '.png'
                with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_image:
                    Imagen.save(temp_image, format=image_format)
                    temp_image_path = temp_image.name

            context = [role, {"mime_type": f"image/{image_format.lower()}", "data": open(temp_image_path, "rb").read()}]

            response = model.generate_content(context)
            response_text = response.text.strip()

            if response_text != 'False':
                try:
                    datos = json.loads(response_text)
                except json.JSONDecodeError as e:
                    return f"Hubo un problema al parsear el JSON {e}"
                except Exception as e:
                    logger.error(f"Ocurrió un error inesperado al procesar el JSON: {e}")
                    return False
                
                try:
                    info_user_with_ia.nameUser = datos["Nombre Completo"]
                    info_user_with_ia.documentUser = datos["Documento"]
                    info_user_with_ia.experienceUser = datos["Experiencia"]
                    info_user_with_ia.placeUser = datos["Direccion Domiciliaria"]
                    info_user_with_ia.save()
                    print("Datos guardados en info_user_with_ia:", info_user_with_ia.nameUser, info_user_with_ia.documentUser, info_user_with_ia.experienceUser, info_user_with_ia.placeUser)
                    return True
                except Exception as e:
                    logger.error(f"Error al guardar los datos del usuario: {e}")
                    return False
                finally:
                    if os.path.exists(temp_image_path):
                        os.remove(temp_image_path)
            else:
                return False
        else:
            return False

    except requests.exceptions.RequestException as e:
        logger.error(f"Error al descargar el archivo desde mediaUrl: {e}")
        return False
    except Exception as e:
        logger.error(f"Error al validar con Gemini: {e}")
        return False



@login_required
def home(request):
    admins = request.user
    usuarios = WhatsappUser.objects.all()  
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')
    print(f"TWILIO_ACCOUNT_SID: {settings.TWILIO_ACCOUNT_SID}")
    print(f"TWILIO_AUTH_TOKEN: {settings.TWILIO_AUTH_TOKEN}")

    
    if fecha_inicio and fecha_fin:
        try:
            fecha_uno = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            fecha_dos = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            usuarios = WhatsappUser.objects.filter(dateRequestUser__date__range=[fecha_uno, fecha_dos])
            print("Usuarios filtrados:", usuarios)
        except ValueError as e:
            print(f"Error al procesar fechas: {e}")
            return HttpResponse("El formato de fechas no fue válido")
    
    # Solo crear gráfico si hay usuarios
    if usuarios.exists():
        fechas = usuarios.values_list('dateRequestUser', flat=True)
        df = pd.DataFrame(fechas, columns=['fecha'])
        df['fecha'] = pd.to_datetime(df['fecha']).dt.date
        
        conteo_fechas = df['fecha'].value_counts().sort_index()
        
        fig, ax = plt.subplots(figsize=(10, 6))  # Tamaño ajustable
        ax.plot(conteo_fechas.index, conteo_fechas.values, marker='h', linestyle='-', color='#1F3361')
        ax.set_title('Mensajes por día')
        ax.set_xlabel('Fecha')
        ax.set_ylabel('Cantidad de mensajes')
        
        buffer = io.BytesIO()
        plt.tight_layout()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        grafico = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)  
        
        print('conteo de fechas:', conteo_fechas)
    else:
        grafico = None

    total_mensajes = usuarios.count()
    
    context = {
        'grafico': grafico,
        'fecha_inicio': fecha_inicio,
        'fecha_fin': fecha_fin,
        'total': total_mensajes,
        'admins': admins,
    }
    
    return render(request, 'home.html', context)

#Chat WhatsApp
#Procedimiento para empezar chat por parte del bot 
@login_required
def Whatsapp(request):
    """Se debe des-armar en mini funciones, hace de todo la pobre :c"""
    form = SendForm()
    form_message_template = CreateNewMessageTemplate()
    form_upload_file = UploadFileForm()

    usuario = request.user
    sede = usuario.place
    messagestemplates = MessageTemplate.objects.filter(place=sede)
    hojas_info = UploadedFile.objects.filter(place=sede)  # Usar directamente los archivos de la BD

    if request.method == 'POST':
        if 'send_message' in request.POST:
            form = SendForm(request.POST)
            if form.is_valid():
                body_message = form.cleaned_data['body_message']
                client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

                # Obtener el archivo seleccionado (ejemplo: primer archivo)
                if hojas_info.exists():
                    archivo_seleccionado = hojas_info.first()  # O usar lógica para selección del usuario
                    full_route = archivo_seleccionado.file.path  # Ruta absoluta del archivo

                    hojaCalculo = pd.read_excel(full_route)
                    if 'Celular' in hojaCalculo.columns:
                        celular = hojaCalculo['Celular'].dropna().astype(str)
                        celular_filter = celular[celular.str.startswith('57')]

                        enviado_a = []
                        for numero in celular_filter:
                            try:
                                message = client.messages.create(
                                    body=f"{body_message}",
                                    from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
                                    to=f"whatsapp:+{numero}"
                                )
                                enviado_a.append(numero)
                            except Exception as e:
                                print(f"Error al enviar mensaje a {numero}: {e}")

                        status_message = "Envio Exitoso" if enviado_a else "Envio Fallido"
                    else:
                        status_message = "La columna 'Celular' no existe en el Excel."
                else:
                    status_message = "No hay archivos subidos."

                return render(request, 'whatsapp.html', {
                    'form': form,
                    'formMessageTemplate': form_message_template,
                    'messageTemplates': messagestemplates,
                    'formUploadFile': form_upload_file,
                    'status_message': status_message,
                    'hojas_info': hojas_info,
                })

        elif 'upload_excel' in request.POST:
            form_upload_file = UploadFileForm(request.POST, request.FILES)
            if form_upload_file.is_valid():
                upload_file = form_upload_file.save(commit=False)
                upload_file.place = sede
                upload_file.save()  # Guarda en la base de datos
                return redirect('whatsapp')

        elif 'create_template' in request.POST:
            form_message_template = CreateNewMessageTemplate(request.POST)
            usuario = request.user
            sede = usuario.place
            if form_message_template.is_valid():
                mensaje_template = form_message_template.save(commit=False)
                mensaje_template.place = sede
                form_message_template.save()
                return redirect('whatsapp')
            
        elif 'delete_file' in request.POST:
            file_id = request.POST.get('file_id')
            try:
                file_to_delete = UploadedFile.objects.get(id=file_id, place=sede)
                file_to_delete.delete() 
                messages.success(request, "¡Archivo eliminado correctamente!")
            except UploadedFile.DoesNotExist:
                messages.error(request, "El archivo no existe o no tienes permisos.")
            
            return redirect('whatsapp')
            
    return render(request, 'whatsapp.html', {
        'form': form,
        'formMessageTemplate': form_message_template,
        'messageTemplates': messagestemplates,
        'formUploadFile': form_upload_file,
        'hojas_info': hojas_info,  # Ahora son objetos de UploadedFile
    })

#funcion para manejar las entradas de usuario por medio de Whatsapp
@csrf_exempt
def handleWhatsapp(request):
    """ Funcion para manejar la entrada de mensajes por medio de WhatsApp """
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    if request.method == 'POST':
        try:
            userInput = request.POST.get('Body', '').strip().lower()
            userSender = request.POST.get('From', '')
            mediaType = request.POST.get('MediaContentType0')
            mediaUrl = request.POST.get('MediaUrl0')
            
            logger.info(f"Datos recibidos - From: {userSender}, Body: {userInput}, Media: {mediaType}")

            if not userInput and not mediaType:
                return JsonResponse({'error': 'Entrada vacía o inválida.'}, status=400)

            user, created = WhatsappUser.objects.get_or_create(phoneNumberUser=userSender)
            
            botResponse = procesar_entrada_usuario(user, userInput, mediaType, mediaUrl)

            message = client.messages.create(
                body=botResponse,
                from_="whatsapp:+14155238886",
                to=userSender
            )
            return JsonResponse({'message_sid': message.sid})
            
        except Exception as e:
            logger.error(f"Error en webhook: {str(e)}", exc_info=True)
            return JsonResponse({'error': 'Error interno del servidor'}, status=500)
    
    elif request.method == 'GET':
        return HttpResponse("Webhook de WhatsApp está funcionando correctamente!", content_type='text/plain')

    return JsonResponse({'error': 'Método no permitido'}, status=405)


def guardarArchivos(user, mediaUrl, mediaType):
    response = requests.get(mediaUrl, auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN))

    # Verifica si la respuesta de la API contiene datos
    print("HTTP Status Code:", response.status_code)
    print("Content-Type:", response.headers.get("Content-Type"))
    print("Content-Length:", len(response.content)) 


    if response.status_code == 200 and len(response.content) > 0:  
        safe_phone_number = re.sub(r'[^\w\-]', '_', user.phoneNumberUser)
        
        if mediaType == 'application/pdf':
            ext = 'pdf'
        elif mediaType.startswith("image/"):
            ext = mediaType.split("/")[-1]
            if ext == "jpeg":
                ext = "jpg"
        elif mediaType == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            ext = "docx"
        else:
            ext = "bin"  # Valor por defecto para otros tipos
       
        file_name = f"{safe_phone_number}.{ext}"
        file_path = os.path.join(settings.MEDIA_ROOT, "user_files", file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "wb") as f:
            f.write(response.content)

        user.cvUser = f"user_files/{file_name}"  # Guarda la ruta en la BD
        user.save()
        try:
            user.cvUser = f"user_files/{file_name}"
            user.save(update_fields=['cvUser'])
        except Exception as e:
            logger.error(f"Error al guardar en la base de datos: {e}")
            return False, f"No se pudo actualizar la base de datos: {str(e)}"
        

        print(f"Archivo guardado en: {file_path}")  # Confirmación

        success_message = "Tu documento se ha guardado exitosamente \n\n"

        return True, success_message
    else:
        return False, "No se pudo guardar el archivo :(. Te pedimos intentar nuevamente"


def procesar_entrada_usuario(user, userInput, mediaType=None, mediaUrl=None):
    print(mediaType)
    id_user_file = user.id
    if mediaUrl:
        if mediaType == "application/pdf":
            ai_validated_file = ai_validate_file_function(mediaUrl, mediaType, id_user_file)
            if ai_validated_file:
                user.refresh_from_db() #refresacar la bd para traer los neuevos datos
                success, message = guardarArchivos(user, mediaUrl, mediaType)
                user.refresh_from_db()
                if success:
                    user.estado = "postulacion_completa_con_archivo"
                    user.save()
                    return (
                        "Hola! Mucho gusto, soy tu asistente virtual.*Te confirmo que tu archivo fue registrado en el sistema* 😊\n\n"
                        "Te socilito que ahora digites la sede a la cual deseas aplicar con tu Archivo \n"
                        "3️⃣ *Carmen de Viboral*: Aguas Claras 🏠\n"
                        "4️⃣ *Rionegro - San Antonio de Pereira*: Caribe 🏠\n"
                        "5️⃣ *La Ceja - Rionegro*: Manantiales 🏠\n"
                        "6️⃣ *Rionegro - Retiro*: Olas 🏠"
                    )
                else:
                    return "Ha ocurrido un error al guardar el archivo. *Intenta nuevamente*"
            else:
                return (
                    "Tu archivo no se reconoce como una Hoja de vida ☹️ \n\n"
                    "Te recuerdo que el archivo que subas a este chat, debe de tener la siguiente información: \n"
                    "*1)* Nombre completo \n"
                    "*2)* Cedula de Ciudadania \n"
                    "*3)* Experiencia *(en caso de No contar con experiencia, no escribas nada)* \n"
                    "*4)* Residencia *(asegúrate de incluir el barrio y ciudad o municipio) *"
                        )
        elif mediaType.startswith("image/"):
            ai_validated_file = ai_validate_file_function(mediaUrl, mediaType, id_user_file)
            if ai_validated_file:
                user.refresh_from_db() #refresacar la bd para traer los neuevos datos
                success, message = guardarArchivos(user, mediaUrl, mediaType)
                if success:
                    user.estado = "postulacion_completa_con_archivo"
                    user.save()
                    return (
                        "Hola! Mucho gusto, soy tu asistente virtual.*Te confirmo que tu archivo fue registrado en el sistema* 🌻😊\n\n"
                        "Te socilito que ahora digites la sede a la cual deseas aplicar con tu Archivo \n"
                        "3️⃣ *Carmen de Viboral*: Aguas Claras 🏠\n"
                        "4️⃣ *Rionegro - San Antonio de Pereira*: Caribe 🏠\n"
                        "5️⃣ *La Ceja - Rionegro*: Manantiales 🏠\n"
                        "6️⃣ *Rionegro - Retiro*: Olas 🏠"
                    )
                else:
                    return "Ha ocurrido un error al guardar el archivo. *Intenta nuevamente*"
            else:
                return (
                    "Tu archivo no se reconoce como una Hoja de vida ☹️ \n\n"
                    "Te recuerdo que el archivo que subas a este chat, debe de tener la siguiente información: \n"
                    "*1)* Nombre completo \n"
                    "*2)* Cedula de Ciudadania \n"
                    "*3)* Experiencia *(en caso de No contar con experiencia, no escribas nada)* \n"
                    "*4)* Residencia *(asegúrate de incluir el barrio y ciudad o municipio) *"
                    )
        elif mediaType == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            ai_validated_file = ai_validate_file_function(mediaUrl, mediaType, id_user_file)
            print("validacion ia:" + str(ai_validated_file))
            if ai_validated_file:
                user.refresh_from_db()
                success, message = guardarArchivos(user, mediaUrl, mediaType)
                if success:
                    user.estado = "postulacion_completa_con_archivo"
                    user.save()
                    return (
                        "Hola! Mucho gusto, soy tu asistente virtual.*Te confirmo que tu archivo fue registrado en el sistema* 🌻😊\n\n"
                        "Te socilito que ahora digites la sede a la cual deseas aplicar con tu Archivo \n"
                        "3️⃣ *Carmen de Viboral*: Aguas Claras 🏠\n"
                        "4️⃣ *Rionegro - San Antonio de Pereira*: Caribe 🏠\n"
                        "5️⃣ *La Ceja - Rionegro*: Manantiales 🏠\n"
                        "6️⃣ *Rionegro - Retiro*: Olas 🏠"
                    )
                else:
                    return "Ha ocurrido un error al guardar el archivo. *Intenta nuevamente*"
            else:
                return (
                    "Tu archivo no se reconoce como una Hoja de vida ☹️ \n\n"
                    "Te recuerdo que el archivo que subas a este chat, debe de tener la siguiente información: \n"
                    "*1)* Nombre completo \n"
                    "*2)* Cedula de Ciudadania \n"
                    "*3)* Experiencia *(en caso de No contar con experiencia, no escribas nada)* \n"
                    "*4)* Residencia *(asegúrate de incluir el barrio y ciudad o municipio) *"
                )
        else:
            return ("Hola! Mucho gusto, soy tu asistente virtual. No reconocozco el tipo de archivo☹️. *Recuerda que los formatos aceptados son; Word, Pdf e imagen*")

    if user.estado is None:
        user.estado = "menu_principal"
        user.save()
        return ("Hola! Soy tu asistente virtual en WhatsApp de *Flores El Trigal* ☺🌻 \n\n"
                "Si deseas aplicar a una oferta laboral y agilizar tu proceso, sube tu *Hoja de Vida* 📄(Preferencial PDF). Asegúrate que el documento contenga toda la información importante Y necesaria. \n\n"
                "*Si subes tu Hoja de Vida, ¡IGNORA EL SIGUIENTE MENU! ⚠* \n\n"

                "☰ *MENÚ*:\n"
                "Escribe el número según sea tu caso: \n"
                "1️⃣ Deseo llenar mis datos y aplicar a una oferta laboral manualmente por este Chat de WhatsApp  🏵️\n"
                "2️⃣ Hablar con un *BILLI* (BOT con IA) 🤖 *\n\n"
                "Estamos aquí para ayudarte.")

    if user.estado == "menu_principal":
        if userInput == '1' or mediaUrl:
            user.estado = "seleccion_sede"
            user.save()
            return ("Digita la sede a la que desees aplicar \n\n"
                    "3️⃣ Aguas Claras - *Carmen de viboral*   🏠 \n"
                    "4️⃣ Caribe - *Rionegro, san Antonio de Pereira*  🏠 \n"
                    "5️⃣ Manantiales - *La Ceja - Rionegro* 🏠 \n"
                    "6️⃣ Olas - *Llanogrande, Rionegro*  🏠")
        elif userInput == '2' or userInput.lower() == 'asesor':
            user.estado = "asesor"
            user.save()
            return ("*Por favor formula tu pregunta.* *BILLI* tratará de darte la respuesta más adecuada.")
        else:
            return "Opción no válida. Por favor, elige una opción del menú (1 o 2)."

    elif user.estado == "seleccion_sede":
        if userInput in ['3', '4', '5', '6']:
            sede_id = 0
            if userInput == '3':
                sede_id = 1
            elif userInput == '4':
                sede_id = 2
            elif userInput == '5':
                sede_id = 3
            elif userInput == '6':
                sede_id = 4

            place_instance = get_object_or_404(PlaceTrigal, id=sede_id)  

            user.placeTrigal = place_instance  
            user.estado = "solicitar_documento"
            user.save()
            return (
                "Haz escogido tu sede 🏠✅. *Ahora por favor digita tu número de cédula de ciudadanía.*"
                "*Por favor escribe por este chat tu cédula SIN ESPACIOS, PUNTOS O COMAS 🪪.*"
                )
        else:
            return "Opción no válida ❌. Por favor, elige una sede digitando 3, 4, 5 o 6."
        
    elif user.estado == "postulacion_completa_con_archivo":
        user.estado = "postulacion_completa" 
        if userInput in ['3', '4', '5', '6']:
            sede_id = 0
            if userInput == '3':
                sede_id = 1
            elif userInput == '4':
                sede_id = 2
            elif userInput == '5':
                sede_id = 3
            elif userInput == '6':
                sede_id = 4

            place_instance = get_object_or_404(PlaceTrigal, id=sede_id)  

            user.placeTrigal = place_instance  
            user.save()
            return(
                "*¡Tu postulación ha sido exitosa! Te noficaremos pronto*. \n\n"
                "Gracias por comunicarte con Flores El Trigal. 😊🌸"
            )
        else:
            return "Opción no válida ❌. Por favor, elige una sede digitando 3, 4, 5 o 6."
    
    elif user.estado == "solicitar_documento":
        if userInput.isdigit(): # .isdigit valida que realmente se un entero
            user.documentUser = userInput
            user.estado = "solicitar_nombre"
            user.save()
            return "Documento registrado exitosamente 🪪✅. *Por favor escribe tu nombre completo en un solo mensaje ✍🏻.*"
        else:
            return "No es valido ❌. *Recuerda solo escribir el número de cédula SIN ESPACIOS, PUNTOS O COMAS* "

    
    elif user.estado == "solicitar_nombre":
        user.nameUser = userInput
        user.estado = "solicitar_experiencia"
        user.save()
        return f"Hola *{user.nameUser}* 😉. Si cuentas con experiencia y deseas agregarla escribe *'Sí'*, de lo contrario escribe *'No'*"
    
    elif user.estado == "solicitar_experiencia":
        if userInput == 'Si' or userInput == 'sI' or userInput == 'si' or userInput == 'SI' or userInput == 'Sí' or userInput == 'sÍ' or userInput == 'sí' or userInput == 'SÍ' :
            user.estado = "solicitar_experiencia_interes"
            user.save()
            return "*POR FAVOR INGRESA TU EXPERIENCIA EN UN SOLO MENSAJE*"
        elif userInput == 'No' or userInput == 'nO' or userInput == 'no' or userInput == 'NO':
            user.estado = "solicitar_direccion"
            user.experienceUser = 'El usuario ha escrito "No" para la experiencia'
            user.save()
            return "Anotado, *Ahora, por favor, en un solo mensaje ingresa la información de tu dirección domiciliaria; asegúrate de incluir el barrio y ciudad o municipio* 🏙️"
        else:
            return('No entendi tu mensaje ☹️. Recuerda solo escribir "*Si*" para agregar experiencia, de lo contario escribe "*No*"')
    
    elif user.estado == "solicitar_experiencia_interes":
        user.experienceUser = userInput
        user.estado = "solicitar_direccion"
        user.save()
        return "*Hemos tomado nota de tu experiencia ✍🏻✅. Ahora en un solo mensaje ingresa la información de tu dirección domiciliaria, asegúrate de incluir el barrio y ciudad o municipio* ↗🏙️"

    elif user.estado == "solicitar_direccion":
        user.placeUser = userInput
        user.estado = "solicitar_cv"
        user.save()
        return "*Si deseas agrega una Hoja de vida📄💼 (Súbela a este chat)*, o escribre *'finalizar'* para continuar."
    
    elif user.estado == "solicitar_cv":
        if userInput.lower() == "finalizar":
            user.estado = "postulacion_completa"
            user.save()
            return ("Tu postulación ha sido completada satisfactoriamente. Te recomendamos estar pendiente del teléfono, te notificaremos lo antes posible. "
            "Gracias por comunicarte con Flores El Trigal. 😊🌸"
            )
        elif mediaUrl:
            success, message = guardarArchivos(user, mediaUrl, mediaType)
            if success:
                user.estado = "postulacion_completa"
                user.save()
                return ("Tu postulación ha sido completada satisfactoriamente. Te recomendamos estar pendiente del teléfono, te notificaremos lo antes posible"
            )
            else:
                return f"Error al procesar tu archivo : {message} ☹️📄❌. Intenta nuevamente o escribe 'finalizar'."
        else: 
            return "*Opción NO válida ❌.* Por favor envía tu hoja de vida por este chat📄💼 o escribe 'finalizar' para continuar."
        
    elif user.estado == "asesor" or user.estado == 'cargo_documento':
        print('ya esta con el asesor')
        try:
            respuesta = MessagingAI(userInput)
            print("respuesta ia:" + str(respuesta))
            return respuesta
        except Exception as e:
            return "El asesor virtual no está disponible en este momento. Intenta más tarde. 🙏"


    elif user.estado == "postulacion_completa":
        user.estado = "menu_principal"
        user.save()
        return ("Ya haz terminado el proceso para aplicar a una oferta laboral \n"
        "Recuerda escribir *2* para hablar con BILLI y responder tus preguntas \n\n"
        "Gracias por comunicarte con Flores El Trigal. 😊🌸"
        )

    else:
        # Estado no reconocido, reiniciar
        user.estado = "menu_principal"
        user.save()
        return "Hubo un problema con tu solicitud. Por favor, intenta nuevamente escribiendo (1) para aplicar a una oferta laboral o (2) para hablar con el asesor "

# Token de verificación (debe coincidir con el que configuraste en Facebook)
VERIFY_TOKEN = "unacadenadetextorandom123"

@csrf_exempt
def webhook(request):
    if request.method == "GET":
        # Verificación del webhook
        hub_mode = request.GET.get("hub.mode")
        hub_token = request.GET.get("hub.verify_token")
        hub_challenge = request.GET.get("hub.challenge")

        if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
            return HttpResponse(hub_challenge, status=200)
        else:
            return HttpResponse("Error de verificación", status=403)

    elif request.method == "POST":
        # Manejo de eventos
        data = json.loads(request.body)
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                # Procesa el evento (por ejemplo, un mensaje)
                sender_id = messaging_event["sender"]["id"]
                if "message" in messaging_event:
                    message_text = messaging_event["message"]["text"]
                    print(f"Mensaje recibido: {message_text} de {sender_id}")
        return HttpResponse("Evento recibido", status=200)

    else:
        return HttpResponse("Método no permitido", status=405)

@login_required
def requestUser(request):
    usuario = request.user
    sede = usuario.place
    sede_id = sede.id

    request_users = WhatsappUser.objects.filter(placeTrigal_id=sede_id)
    if request.method == 'POST':
        usuarioCheck = request.POST.getlist('usuario[]') 
        new_sede = request.POST['select-user-job']
        for x in usuarioCheck:
            seleccionarUsuarios = WhatsappUser.objects.filter(id=x)
            for z in seleccionarUsuarios:
                z.placeTrigal_id = new_sede
                z.save()
    return render(request, 'solicitudes.html', {
        'usuario': request_users,
    })  
            

def descargar_excel(request, sede_id):
    """ Descarga el Excel con los datos de las personas que se han comunicado por Whatsapp"""
    d = WhatsappUser.objects.filter(placeTrigal_id = sede_id).values('phoneNumberUser', 'nameUser', 'documentUser', 'experienceUser', 'dateRequestUser')

    if not d.exists():
        messages.info(request, "Deben existir datos para descargar el Excel")
        return redirect('requestUser')

    df = pd.DataFrame(list(d))

    df['dateRequestUser'] = pd.to_datetime(df['dateRequestUser']).dt.tz_localize(None)

    df = df.rename(columns={
        'phoneNumberUser' : 'Telefono',
        'nameUser' : 'Nombre',
        'documentUser' : 'Documento',
        'experienceUser' : 'Experiencia',
        'dateRequestUser'  : 'Fecha de la Solicitud',
    })

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer: #sintaxis de with : 'with expresion as variable'. With ayuda a que el codigo se cierre de una manera adeacuada
        df.to_excel(writer, index=False, sheet_name='Postulantes')

    response = HttpResponse(
        buffer.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename=Postulantes.xlsx'
    return response

def delete_message_template_user_funcion(request, message_template_user_id):
    message = get_object_or_404(MessageTemplate, pk=message_template_user_id)
    if request.method == 'POST':
        message.delete()
        return redirect('whatsapp')

def edit_postulacion_function(request, postulacion_id):
    postulacion_to_edit = get_object_or_404(WhatsappUser, pk=postulacion_id)
    print(postulacion_to_edit.cvUser)

    return render(request, 'solicitudes_edit.html',{
        'postulado' : postulacion_to_edit
    })