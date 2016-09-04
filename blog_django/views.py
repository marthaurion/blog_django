from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.template.loader import get_template
from django.core.mail import send_mail
from django.template import Context
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from blog.models import Category
from .forms import ContactForm

# Create your views here.
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


class AboutView(TemplateView):
    template_name = 'about.html'


class BlogrollView(TemplateView):
    template_name = 'blogroll.html'


class ContactView(FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = '/messagereceived/'
    
    def form_valid(self, form):
        form.send_email()
        return super(ContactView, self).form_valid(form)


class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'