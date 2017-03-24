from django.http import Http404
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils import timezone

from blog.views import CommentFormMixin
from blog.models import Comment

from .forms import ContactForm

# Create your views here.
class BasePageView(CommentFormMixin, TemplateView):
    page_url = '/'
    
    def get(self, request, *args, **kwargs):
        if 'email' in request.GET and 'comment' in request.GET:
            comment_pk = int(request.GET['comment'])
            try:
                comment = Comment.objects.get(pk=comment_pk)
                comment.unsubscribe(request.GET['email'])
            except (Comment.MultipleObjectsReturned, Comment.DoesNotExist):
                pass # again, might want to log here
        return super().get(request, *args, **kwargs)
    
    # override get object so that it gives a 404 error if you're looking at a post in the future and you're not an admin
    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.pub_date>timezone.now(): # don't show future posts
            if not self.request.user.is_active and not self.request.user.is_superuser: # only block if not an admin
                raise Http404()
        return obj
        
    # add comment notify to context from session
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_notify'] = self.request.session.get('comment_notify')
        context['comment_list'] = Comment.objects.filter(approved=True, page_url=self.page_url)
        context['post_comment_url'] = self.page_url
        return context
        
    # override the post function to handle the form values and create a comment
    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.comment_check(request, form, page_url=self.page_url)
        else:
            return self.form_invalid(form)

class AboutView(BasePageView):
    template_name = 'about.html'
    page_url = '/about/'


class BlogrollView(BasePageView):
    template_name = 'blogroll.html'
    page_url = '/blogroll/'


class ContactView(SuccessMessageMixin, FormView):
    template_name = 'contact.html'
    form_class = ContactForm
    success_url = '/contact/'
    success_message = "Message sent. I'll get right on that...eventually."
    
    def form_valid(self, form):
        form.send_email()
        return super().form_valid(form)


class ContactSuccessView(TemplateView):
    template_name = 'contact_success.html'