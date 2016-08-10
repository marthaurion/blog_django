from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.core.mail import send_mail
from django.template import Context
from blog.models import Category
from .forms import ContactForm

# Create your views here.
def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    # process form data if request is a post
    if request.method == 'POST':
        form_class = ContactForm(request.POST)
        if form_class.is_valid():
            name = form_class.cleaned_data['name']
            message = form_class.cleaned_data['message']
            sender = form_class.cleaned_data['sender']
            subject = "New message from: " + name + " at " + sender
            
            recipients = ['marthaurion@gmail.com']
            send_mail(subject, message, sender, recipients)
            return redirect('thanks')
            
    # otherwise jsut display the form
    else:
        form_class = ContactForm()

    return render(request,'contact.html',
                 { 'form': form_class })
                   
def contact_success(request):
    return render(request, 'contact_success.html')
                              
def blogroll_page(request):
    return render(request, 'blogroll.html')