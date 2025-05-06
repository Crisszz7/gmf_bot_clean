from django.shortcuts import render
from .forms import SendNewMessage
from django.http import JsonResponse, HttpResponse
from twilio.rest import Client
from django.contrib.auth.decorators import login_required
from django.conf import settings

# Create your views here.
@login_required
def sms(request):
    formSendNewMessage = SendNewMessage()
    if request.method == 'POST':
        if 'enviar_sms' in request.POST:
            formSendNewMessage = SendNewMessage(request.POST)
            if formSendNewMessage.is_valid():
                body_message = formSendNewMessage.cleaned_data['body']
                account_sid = settings.TWILIO_ACCOUNT_SID
                auth_token = settings.TWILIO_AUTH_TOKEN
                
                client = Client(account_sid, auth_token)

                try:
                    message = client.messages.create(
                    body=f"{body_message}",
                    from_="+14323051474",
                    to=settings.MY_PHONE_NUMBER
                    ) 
                except Exception as e:
                    return f"Algo salio mal"
            
            return JsonResponse({
                    'mensaje' : message.sid
            })
        
    return render(request, 'sms.html', {
        'formSendNewMessage' : formSendNewMessage
    })
    
