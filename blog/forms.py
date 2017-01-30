from django import forms

from .models import Comment, Commenter


attrib = {'class': 'form-control'}

class CommentForm(forms.Form):
    username = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs=attrib))
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs=attrib))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs=attrib))
    text = forms.CharField(required=True, widget=forms.Textarea(attrs=attrib))