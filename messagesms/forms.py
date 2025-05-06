from django import forms

class SendNewMessage(forms.Form):
    body = forms.CharField(max_length=160 ,label="Mensaje:", widget=forms.Textarea(attrs={'class': 'rounded-lg bg-neutral-100 w-9/10 h-2'}), required=True)


    
