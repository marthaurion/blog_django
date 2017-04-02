from datetime import timedelta

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.dispatch import receiver
from django.utils.timezone import localtime
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import urlize
from django.core.exceptions import ImproperlyConfigured
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage

import markdown
import pytz
import hashlib
import uuid
import logging
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
from precise_bbcode.bbcode import get_parser
from akismet import Akismet


logger = logging.getLogger(__name__)

# manager to pull all posts that aren't published in the future
class PostManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(pub_date__lte=timezone.now())

# returns either today at 4pm (server time) or tomorrow at 4pm if it's currently after 4pm
def default_start_time():
    now = localtime(timezone.now())
    start = now.replace(hour=16, minute=0, second=0, microsecond=0)
    if now >= start:
        start = start + timedelta(days=1)
    start = start.astimezone(pytz.utc)
    return start

class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, max_length=300)
    excerpt = models.TextField()
    body = models.TextField()
    body_html = models.TextField(editable=False)
    category = TreeForeignKey('Category', on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', default=default_start_time, db_index=True)
    tags = TaggableManager()
    first_image = VersatileImageField(editable=False, max_length=400)

    objects = models.Manager()
    published = PostManager()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        local_pub_date = localtime(self.pub_date)
        return "/blog/%s/%s/" % (local_pub_date.strftime("%Y/%m/%d"), self.slug)
    
    def approved_comments(self):
        return self.comments.filter(approved=True)
        
    def get_comment_count(self):
        num = self.approved_comments().count()
        if not num:
            return "No comments"
        else:
            return str(num) + " comments"
    
    # takes the text of the post and replaces the {{REPLACE}} strings with the proper image text
    def process_image_links(self, body_parts, word=None):
        link_string = '<a href="%s"><img src="%s" height="%s" width="%s" class="img-responsive" /></a>'
        for i in range(0,len(body_parts)):
            if i%2 == 0: # skip even pieces because they're not surrounded by replace tokens
                continue
            cur_image = body_parts[i]
            try:
                img = Media.objects.get(image_name=cur_image)
                link_text = link_string % (img.full_image.url, img.scale_image.url, img.scale_image.height, img.scale_image.width)
                body_parts[i] = link_text
            except (Media.MultipleObjectsReturned, Media.DoesNotExist):
                logger.error('No media found for image name: %s' % cur_image)
        return "".join(body_parts)
        
    # override save so we can add the linked images to the post
    def save(self, *args, **kwargs):
        body_parts = self.body.split("{{REPLACE}}")
        image_processed = self.process_image_links(body_parts)
        self.body_html = markdown.markdown(image_processed)
        first_img = self.get_first_image()
        if first_img:
            self.first_image = first_img.full_image
        super().save(*args, **kwargs)

    # get the first image from the body text
    def get_first_image(self):
        body_parts = self.body.split("{{REPLACE}}", 2) # only split twice because we're getting the first image, which is the second piece
        if len(body_parts) > 1:
            img_name = body_parts[1]
            try:
                img = Media.objects.get(image_name=img_name) # find the image model
                return img
            except (Media.MultipleObjectsReturned, Media.DoesNotExist):
                logger.error('No media found for image name: %s' % img_name)
        return None
        
    def wordpress_body(self):
        referral = '[Click here](https://www.marthaurion.com%s) to check this post out on my personal website.\n\n' % self.get_absolute_url()
        return markdown.markdown(referral) + self.body_html
        
        
@receiver(models.signals.post_save, sender=Post)
def warm_Post_first_image(sender, instance, **kwargs):
    first = instance.get_first_image()
    if first:
        post_img_warmer = VersatileImageFieldWarmer(
            instance_or_queryset=first,
            rendition_key_set='first_image',
            image_attr='full_image'
        )
        num_created, failed_to_create = post_img_warmer.warm()


class Category(MPTTModel):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children', db_index=True)
    active = models.BooleanField(default=False)

    class MPTTMeta:
        order_insertion_by = ['slug']

    class Meta:
        ordering = ['slug']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return "/blog/category/%s/" % self.slug
    
    def get_display(self):
        if self.active:
            prefix_character = "[&minus;]"
        else:
            prefix_character = "[+]"
        
        if self.is_leaf_node():
            prefix = '&#8212; &nbsp;'
        else:
            prefix = '<a class="collapsible" href="#cat%s">%s</a> &nbsp;' % (self.pk, prefix_character)
        return '<li>%s<a href="%s">%s</a></li>\n' % (prefix, self.get_absolute_url(), self.title)
    
    def get_active_string(self):
        if self.active:
            return "in"
        return ""
        
class Media(models.Model):
    image_name = models.SlugField(max_length=200, unique=True)
    pub_date = models.DateTimeField('date published', default=timezone.now, editable=False)
    full_image = VersatileImageField(upload_to="full/%Y/%m/%d", max_length=400)
    scale_image = VersatileImageField(max_length=400, editable=False)
    
    class Meta:
        verbose_name_plural = "media"
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.image_name
        
    def get_blog_url(self):
        return "/blog/media/"+self.image_name
        
    def get_link_html(self):
        link_string = '<a href="%s"><img src="%s" height="%s" width="%s" class="img-responsive" /></a>'
        if self.full_image is None or self.scale_image is None:
            return '<img src="#" alt="Image not found" />'
        link_string = '<a href="%s"><img src="%s" height="%s" width="%s" class="img-responsive" /></a>'
        return link_string % (self.full_image.url, self.scale_image.url, self.scale_image.height, self.scale_image.width)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        self.scale_image = self.full_image.thumbnail['750x540'].name
        super().save(*args, **kwargs)
    
@receiver(models.signals.post_save, sender=Media)
def warm_Media_images(sender, instance, **kwargs):
    media_img_warmer = VersatileImageFieldWarmer(
        instance_or_queryset=instance,
        rendition_key_set='scaled_image',
        image_attr='full_image'
    )
    num_created, failed_to_create = media_img_warmer.warm()


class Link(models.Model):
    title = models.CharField(max_length=150)
    url = models.URLField()
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['title']
    
    def __str__(self):
        return self.title
        
        
class Mapping(models.Model):
    source = models.URLField()
    dest = models.URLField()
    
    
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
        return base_url + '#comment' + str(self.pk)
        
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
        html_body = render_to_string('blog/comment_body.html', context)
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