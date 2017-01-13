from django.conf import settings
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView
from requests_oauthlib import OAuth2Session

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
    
    
class TestAuth(RedirectView):
    permanent = False
    
    def get_redirect_url(self, *args, **kwargs):
        testing = OAuth2Session(settings.OAUTH_CLIENT_ID, redirect_uri = "https://blank-django-marthaurion.c9users.io/token")
        authorization_url, state = testing.authorization_url('https://public-api.wordpress.com/oauth2/authorize')
        return authorization_url
        

class TestToken(TemplateView):
    template_name = 'testing.html'
    
    def get_context_data(self, **kwargs):
        context = super(TestToken, self).get_context_data(**kwargs)
        code = self.request.GET.get('code')
        testing = OAuth2Session(settings.OAUTH_CLIENT_ID, redirect_uri = "https://blank-django-marthaurion.c9users.io/token")
        token = testing.fetch_token('https://public-api.wordpress.com/oauth2/token', client_secret=settings.OAUTH_CLIENT_SECRET, code=code)
        context['token'] = token['access_token']
        self.request.session['oauth_token'] = token['access_token']
        return context
    
    def get_redirect_url(self, *args, **kwargs):
        code = self.request.GET.get('code')
        testing = OAuth2Session(settings.OAUTH_CLIENT_ID, redirect_uri = "https://blank-django-marthaurion.c9users.io/token")
        token = testing.fetch_token('https://public-api.wordpress.com/oauth2/token', client_secret=settings.OAUTH_CLIENT_SECRET, code=code)
        self.request.session['oauth_token'] = token['access_token']
        return token