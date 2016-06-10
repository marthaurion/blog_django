from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, required=True,
                                widget=forms.TextInput(attrs={'class': 'form-control'}))
    sender = forms.EmailField(label="Email", required=True, 
                                widget=forms.EmailInput(attrs={'class': 'form-control'}))
    message = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control'}))