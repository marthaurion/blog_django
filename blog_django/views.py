from django.http import Http404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, FormMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone
from django.contrib.flatpages.models import FlatPage
import logging

from blog.views import CommentFormMixin
from blog.models import Comment

from .forms import ContactForm

logger = logging.getLogger(__name__)

# Create your views here.
class BasePageView(CommentFormMixin, FormMixin, TemplateView):
    page_url = '/'
    
    def get(self, request, *args, **kwargs):
        if 'email' in request.GET and 'comment' in request.GET:
            self.unsubscribe_comment(request.GET['comment'], request.GET['email'])
        return super().get(request, *args, **kwargs)
        
    # add comment notify to context from session
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_notify'] = self.request.session.get('comment_notify')
        context['comment_list'] = Comment.objects.filter(approved=True, page_url=self.page_url)
        context['post_comment_url'] = self.page_url
        try:
            page = FlatPage.objects.get(url=self.page_url)
            context['flatpage'] = page
        except(FlatPage.MultipleObjectsReturned, FlatPage.DoesNotExist):
            logger.error('Flatpage query failed: %s' % self.page_url)
        return context
        
    # override the post function to handle the form values and create a comment
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.comment_check(request, form, page_url=self.page_url)
        else:
            return self.form_invalid(form)

class AboutView(BasePageView):
    template_name = 'flatpages/about.html'
    page_url = '/about/'


class BlogrollView(BasePageView):
    template_name = 'flatpages/blogroll.html'
    page_url = '/blogroll/'
    
    
class ReviewsView(BasePageView):
    template_name = 'flatpages/reviews.html'
    page_url = '/reviews/'


class ContactView(SuccessMessageMixin, FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = '/contact/'
    success_message = "Message sent. I'll get right on that...eventually."
    
    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)