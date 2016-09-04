from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from .forms import ContactForm

# Create your views here.
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