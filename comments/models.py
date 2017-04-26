from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage

import hashlib
import uuid
import logging
from mptt.models import MPTTModel, TreeForeignKey
from precise_bbcode.bbcode import get_parser
from akismet import Akismet

from blog.models import Post

logger = logging.getLogger(__name__)


class Commenter(models.Model):
    username = models.CharField(max_length=200)
    email = models.EmailField()
    website = models.URLField(blank=True)
    approved = models.BooleanField(default=False)
    spam = models.BooleanField(default=False)
    
    def approve(self):
        self.approved = True
        for comment in Comment.objects.filter(author=self):
            comment.approve()
        self.save()
    
    def unapprove(self):
        self.approved = False
        for comment in Comment.objects.filter(author=self):
            comment.unapprove()
        self.save()
        
    def mark_spam(self):
        self.spam = True
        for comment in Comment.objects.filter(author=self):
            comment.spam = True
            comment.save()
        self.save()
        
    def mark_safe(self):
        self.spam = False
        for comment in Comment.objects.filter(author=self):
            comment.spam = False
            comment.save()
        self.save()
    
    def get_commenter_text(self):
        if self.website:
            return '<a href="%s">%s</a>' % (self.website, self.username)
        return self.username
    
    def get_profile_url(self):
        email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/%s" % (email_hash)
    
    def get_image_url(self):
        email_hash = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return "https://www.gravatar.com/avatar/%s?s=%s" % (email_hash, str(50))
    
    def __str__(self):
        return self.username


class Comment(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    post = models.ForeignKey(Post, null=True, blank=True, related_name='comments')
    page_url = models.CharField(max_length=100, blank=True)
    approved = models.BooleanField(default=False, db_index=True)
    pub_date = models.DateTimeField('date published', default=timezone.now, editable=False, db_index=True)
    author = models.ForeignKey(Commenter, related_name='comments')
    text = models.TextField(blank=True) # form should force this field anyway, so this is just for the admin
    notify = models.BooleanField(default=False)
    spam = models.BooleanField(default=False)
    html_text = models.TextField(blank=True) # creating this field to take wordpress imported comments because they're formatted in html
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    
    class Meta:
        ordering = ['pub_date']
        
    class MPTTMeta:
        order_insertion_by = ['pub_date']
        
    def __str__(self):
        return str(self.pk)
    
    def get_absolute_url(self):
        if self.post:
            base_url = self.post.get_absolute_url()
        else:
            base_url = self.page_url
        return base_url + '#comment' + str(self.uuid)
        
    def get_unsubscribe_url(self):
        if self.post:
            base_url = self.post.get_absolute_url()
        else:
            base_url = self.page_url
        unsubscribe_query = '?email=%s&comment=%s' % (self.author.email, str(self.uuid))
        return base_url + unsubscribe_query
    
    def approve(self):
        self.approved = True
        self.save()
    
    def unapprove(self):
        self.approved = False
        self.save()
        
    def get_post_title(self):
        if self.post:
            return self.post.title
        # if post isn't set, it's a page, so try to find it
        try:
            page = FlatPage.objects.get(url=self.page_url)
            return page.title
        except(FlatPage.DoesNotExist, FlatPage.MultipleObjectsReturned):
            logger.error('FlatPage query error: %s' % self.page_url)
            
    def save(self, *args, **kwargs): # override save to parse bbcode first
        if self.text:
            parser = get_parser()
            self.html_text = parser.render(self.text)
        super().save(*args, **kwargs)
    
    # if the email passed in matches the author, then turn off notifications
    def unsubscribe(self, email):
        if email == self.author.email:
            self.notify = False
            self.save()
    
    def send_email_notification(self, info_dict, recipients):
        if self.author.email in recipients: # don't send comments to yourself
            recipients.remove(self.author.email)
        if len(recipients) < 1: # if there are no more recipients, quit out
            return
        subject = "New comment on %s" % self.get_post_title()
        comment_url = info_dict['url']
        context = { 'comment_author': self.author.username,
                    'comment_text': self.text,
                    'comment_url': comment_url,
                    'unsubscribe_url': info_dict['unsubscribe']
        }
        body = "Check out the reply to your comment at %s" % comment_url
        html_body = render_to_string('comments/comment_body.html', context)
        msg = EmailMultiAlternatives(subject=subject, from_email="marth@mail.marthaurion.com",
                                    to=recipients, body=body)
        msg.attach_alternative(html_body, "text/html")
        msg.send()
        
    def notify_authors(self):
        if not self.notify:
            return []
        recipients = [self.author.email] # first send the notification to the parent comment's author
        return recipients
    
    def send_notifications(self, info_dict):
        if self.spam_check(info_dict): # don't send notifications for suspected spam
            return
        self.send_email_notification(info_dict, ["marthaurion@gmail.com"]) # first always send notification to me, the admin
        if self.parent and self.approved:
            self.send_email_notification(info_dict, self.parent.notify_authors())
            
    def spam_check(self, info_dict):
        if self.author.spam:
            return True
        
        approved = self.author.approved
        if approved:
            return False
        current_domain = Site.objects.get_current().domain
        user_agent = 'Marth Blog/0.0.1'
        akismet = Akismet(settings.AKISMET_KEY, 'http://{0}'.format(current_domain), user_agent)
        is_spam = akismet.check(info_dict['remote_addr'],
                                info_dict['user_agent'],
                                comment_author=self.author.username,
                                comment_author_email=self.author.email,
                                comment_author_url=self.author.website,
                                comment_content=self.text)
        if is_spam:
            self.author.mark_spam()
        return is_spam
        
    def get_request_info(self, request):
        info_dict = {}
        info_dict['url'] = request.build_absolute_uri(self.get_absolute_url())
        info_dict['unsubscribe'] = request.build_absolute_uri(self.get_unsubscribe_url())
        info_dict['remote_addr'] = request.META.get('REMOTE_ADDR')
        info_dict['user_agent'] = request.META.get('HTTP_USER_AGENT')
        return info_dict