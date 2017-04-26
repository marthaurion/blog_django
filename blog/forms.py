from django import forms
from .models import Media


class BulkMediaForm(forms.Form):
    name = forms.CharField(max_length=200, required=True)
    images = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))