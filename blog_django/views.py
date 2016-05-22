from django.shortcuts import render_to_response, render, redirect
from django.template.loader import get_template
from django.core.mail import send_mail
from django.template import Context
from blog.models import Category
from .forms import ContactForm

# Create your views here.
def about_page(request):
    return render_to_response('about.html',
                              { 'categories': Category.objects.filter(parent__isnull=True) })

def contact_page(request):
    form_class = ContactForm()

    return render(request,'contact.html',
                 { 'categories': Category.objects.filter(parent__isnull=True),
                   'form': form_class })