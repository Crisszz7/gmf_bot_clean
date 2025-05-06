from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import AdminWebUser, MessageAI

class CustomCreationUserForm(UserCreationForm):
    email = forms.EmailField(max_length=100, required=True, label="Correo")
    class Meta:
        model = AdminWebUser
        fields = ["username","email", "place" , "password1", "password2"]
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo',
            'place': 'Sede que administra el usuario',
            'password1': 'Contraseña',
            'password2': 'Repite la contraseña',
        }
        widgets= {
            'username' : forms.TextInput(attrs={
                'class' : 'w-full bg-neutral-100 m-3 rounded',
                'placeholder' : 'Nombre de usuario',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(CustomCreationUserForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class' : 'w-full bg-neutral-100 m-3 rounded'})
        self.fields['place'].widget.attrs.update({'class': 'w-full bg-neutral-100 m-3 rounded'})
        self.fields['password1'].widget.attrs.update({'class': 'w-full bg-neutral-100 m-3 rounded'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full bg-neutral-100 m-3 rounded'})

class MessageAIForm(forms.ModelForm):
    class Meta:
        model = MessageAI
        fields = ['ask', 'answer']
        labels = {
            'ask': 'Escribe la pregunta aquí',
            'answer': 'Escribe la respuesta correspondiente aquí',
        }
        widgets = {
            'ask': forms.TextInput(attrs={
                'class': 'border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500 m-2',
                'placeholder': 'Plantea la pregunta aqui!'
            }),
            'answer': forms.Textarea(attrs={
                'class': 'border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-green-500 m-2',
                'placeholder': 'Escribe aca la respuesta correspondiente...'
            }),
        }