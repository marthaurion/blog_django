from django import forms
from .models import Media

class CommentForm(forms.Form):
    username = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label="Email", required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    website = forms.URLField(required=False, widget=forms.URLInput(attrs={'class': 'form-control'}))
    text = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'comment-form-text'}))
    parent = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'comment-form-parent'}))


class BulkMediaForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))