from django.utils import timezone
from django.conf import settings

import logging
import datetime

from .models import Comment, Commenter
from .forms import CommentForm
from .tasks import send_email

logger = logging.getLogger(__name__)


class CommentFormMixin(object):
    form_class = CommentForm
    
    # override initial values for the form to use session values for a commenter if they exist
    def get_initial(self):
        return { 'username': self.request.session.get('comment_username'),
                'email': self.request.session.get('comment_email'),
                'website': self.request.session.get('comment_website') }

    def comment_check(self, request, form, post=None, page_url=''):
        form_email = form.cleaned_data['email']
        form_username = form.cleaned_data['username']
        form_website = form.cleaned_data['website']
        try:
            author = Commenter.objects.get(email=form_email)
            changed = False
            # if username or website are changed, update them for the author of the comment
            if form_website and form_website != author.website:
                author.website = form_website
                changed = True
            if form_username and form_username != author.username:
                author.username = form_username
                changed = True
            if changed:
                author.save()
        except Commenter.DoesNotExist: # if no commenter is found for the email in the form, create one
            author = Commenter()
            author.email = form_email
            author.username = form_username
            author.website = form_website
            author.save()
        except Commenter.MultipleObjectsReturned: # probably shouldn't happen, but here just in case
            logger.error('Multiple commenters found for email: %s' % form_email)
            return self.form_invalid(form)
        
        request.session['comment_email'] = author.email  # save commenter information in a session so it can be reused later
        request.session['comment_username'] = author.username
        request.session['comment_website'] = author.website
        
        # prep comment fields before creating the new comment
        parent = None
        if form.cleaned_data['parent']:
            parent_id = form.cleaned_data['parent'].replace('#comment','')
            try:
                parent = Comment.objects.get(uuid=parent_id)
            except (Comment.MultipleObjectsReturned, Comment.DoesNotExist):
                logger.error('Invalid parent comment id: %d' % parent_id)
        comment_notify = bool(request.POST.get('notify', False))
        
        search_time = timezone.now()-datetime.timedelta(seconds=10)
        # try to find the same comment in the last 10 seconds or create a new one otherwise
        comment, created = Comment.objects.get_or_create(
            parent=parent,
            post=post, # this will be None if it's a page
            page_url=page_url, # this will be an empty string if it's a post
            pub_date__gt=search_time,
            text=form.cleaned_data['text'],
            author=author,
            approved=author.approved,
            notify=comment_notify,
            spam=author.spam
        )
        self.success_url = comment.get_absolute_url()
        if not created: # if this is a duplicate, return without notification
            return self.form_valid(form)
        
        request.session['comment_notify'] = comment_notify # log notification setting in the session
        
        request_info = comment.get_request_info(request)
        if settings.DEV_SERVER: # can't set up celery on cloud9, so running the standard email
            comment.send_notifications(request_info)
        else:
            send_email.delay(comment.pk, request_info)
        return self.form_valid(form)
        
    def unsubscribe_comment(self, uuid, email):
        try:
            comment = Comment.objects.get(uuid=uuid)
            comment.unsubscribe(email)
        except (Comment.MultipleObjectsReturned, Comment.DoesNotExist):
            logger.error('Email unsubscribe failed for comment: %d' % uuid)