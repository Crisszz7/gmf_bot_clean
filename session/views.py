from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import  login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .models import AdminWebUser, MessageAI
from messagewpp.models import PlaceTrigal
from .forms import CustomCreationUserForm, MessageAIForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password



def obtener_formularios():
    return {
        "userCreationForm" : CustomCreationUserForm(),
        "userLoginForm" : AuthenticationForm(),
        "MessageAIForm" : MessageAIForm,
    }



def login_function(request):
    if request.method == 'GET':
        formularios = obtener_formularios()
        return render(request, 'login.html',{
            **formularios,
            'title' : 'Flores El Trigal GMF',
        })
    else: 
        formularios = obtener_formularios()
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is None:
            return render(request, 'login.html', {
                **formularios,
                'message' : 'Nombre de usuario o contraseña no validos.',
                'title' : 'Flores El Trigal',
            })
        else:
            if user.username == 'admin':
                login(request, user)
                return redirect('message-ai')
            else:
                login(request, user)
                return redirect('home')
        

def sign_up_function(request):
    if request.method == 'GET':
        formularios = obtener_formularios()
        sedes_con_emails = []
        exists_places = AdminWebUser.objects.all()

        for s in exists_places:
            id = s.id
            username = s.username
            sede = s.place
            if sede.namePlace != 'Trigal':
                print("if")
                sedes_con_emails.append({
                    'id' : id,
                    'username': username,
                    'sede': sede,
                    'emails': [ocultar_email(user.email) for user in AdminWebUser.objects.filter(place=sede)],
                })
            else:
                continue

            print(sedes_con_emails)


        return render(request, 'signup.html', {
            **formularios,
            'sedes_con_emails': sedes_con_emails
        })
    else:
       if request.POST['password1'] == request.POST['password2']:
           try:
                place_id = request.POST.get('place', None)
                place = None

                if place_id:
                    place = PlaceTrigal.objects.get(id=place_id)

                if AdminWebUser.objects.filter(place = place).exists():
                    messages.error(request, "Un administrador ya existe para esa sede")
                    return redirect('sign_up')

                user = AdminWebUser.objects.create_user(
                    username=request.POST['username'],
                    password=request.POST['password1'], 
                    email=request.POST['email'],
                    place = place,
                    is_superuser = False,
                    is_staff = False,
                )

                if AdminWebUser.objects.filter(username = username).exists:
                    messages.error(request, "Ya existe un usuario con ese nombre")
                    return redirect('sign_up')

                user.save()
                messages.success(request, 'El registro ha sido exitoso')
                return redirect('sign_up')
           except Exception as e:
                HttpResponse(f"salio mal: {e}" )
                return redirect( 'sign_up')
       else:
           messages.info(request, 'Las contraseñas deben ser iguales ')
           return redirect('sign_up')

@login_required
def messages_ai_function(request) -> redirect:
    ai_message_list = MessageAI.objects.all()
    if request.method == 'POST':
        form = MessageAIForm(request.POST)
        if form.is_valid():
            form.save()
            form = MessageAIForm() 
            return redirect('message-ai') 
        else:
            return render(request, 'AI.html', {
                'form': form
            })
    else:
        form = MessageAIForm()
        return render(request, 'AI.html', {
            'form': form,
            'ai_message_list' : ai_message_list
        })


def logout_function(request):
    logout(request)
    return redirect('login')

def details_edit_message_ai_function(request, message_ai_id):
    if request.method == 'GET':
        message_ai = get_object_or_404(MessageAI, pk=message_ai_id)
        form = MessageAIForm(instance=message_ai)
        return render(request, 'AI_message.html', {
            'message_ai' :message_ai,
            'form' : form,
        })
    elif request.method == 'POST' and 'edit-cancel-button' in request.POST :
            return redirect('message-ai')
    elif request.method == 'POST' and 'edit-confirm-button' in request.POST :
        try:
            message_ai = get_object_or_404(MessageAI, pk=message_ai_id)
            form = MessageAIForm(request.POST, instance=message_ai)
            form.save()
            print('edit')
            return redirect('message-ai')
        except ValueError:
            return render(request, 'AI_message.html',{
            'tarea' :message_ai,
            'form' : form,
            'error' : 'Tienes un error!',
        })

def delete_place_admin_function(request, admin_id):
    formularios = obtener_formularios
    if request.method == 'POST':
        admin_pk = admin_id
        admin_delete = get_object_or_404(AdminWebUser, id=admin_pk)
        password_input = request.POST.get('password-confirm-delete')
        password_admin_saved = admin_delete.password
        if check_password(password_input, password_admin_saved):
            admin_delete.delete()
            messages.success(request, "Usuario eliminado exitosamente!")
            return redirect('sign_up')
        else:
            messages.error(request, "La contraseña no es correcta")
            return redirect('sign_up')
    return render(request, 'signup.html', {
            **formularios,
        })

def delete_message_ai_function(request, message_ai_id):
    message_ai = get_object_or_404(MessageAI, pk=message_ai_id)
    print(message_ai)
    if request.method == 'POST':
        message_ai.delete()
        return redirect('message-ai')
    
    

def ocultar_email(admin_email):
    nombre, dominio = admin_email.split("@")
    if len(nombre) > 1:
        return nombre[0] + "****@" + dominio
    else:
        return nombre + '***' + '@' + dominio
    

    



        




