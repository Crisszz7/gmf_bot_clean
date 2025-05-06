from django import forms
from .models import MessageTemplate, UploadedFile


class SendForm(forms.Form):
        body_message = forms.CharField(
        label="Mensaje:", 
        max_length=1000, 
        required=True, 
        widget=forms.Textarea(attrs={
            "ondrop": "drop(event)", 
            "ondragover": "allowDrop(event)",
            'class': 'rounded-lg bg-neutral-100 w-full',
        })
    )
    
class CreateNewMessageTemplate(forms.ModelForm):
    class Meta:
        model = MessageTemplate
        fields = ['title', 'body']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'rounded-lg w-xl  '}),
            'body': forms.Textarea(attrs={'class': 'rounded-sm form-control'}),
        }

class UploadFileForm(forms.ModelForm):
     class Meta:
          model = UploadedFile
          fields = ['title', 'file']
          labels = {
            'title': 'Nombre del archivo',
            'file': 'Archivo'   
          }
          widgets = {
            'title': forms.TextInput(attrs={'class': ' bg-neutral-100 m-3 rounded w-11/12'}),
            'file' : forms.FileInput(attrs={'class' : 'rounded bg-blue-300 p-2 '})
        }