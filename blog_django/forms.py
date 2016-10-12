from django import forms
from django.core.mail import send_mail
from captcha.fields import CaptchaField

attrib = {'class': 'form-control'}

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs=attrib))
    sender = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs=attrib))
    message = forms.CharField(required=True, widget=forms.Textarea(attrs=attrib))
    captcha = CaptchaField()
    
    def send_email(self):
        name = self.cleaned_data['name']
        message = self.cleaned_data['message']
        sender = self.cleaned_data['sender']
        subject = "New message from: " + name + " at " + sender
        
        recipients = ['marthaurion@gmail.com']
        send_mail(subject, message, sender, recipients)