from django import forms

class ContactForm(forms.Form):
    sender = forms.EmailField(label="E-mail", required=True)
    subject = forms.CharField(max_length=100, required=True)
    message = forms.CharField(widget=forms.Textarea, required=True)