from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.utils.timezone import localtime

import markdown
import pytz
import logging
from mptt.models import MPTTModel, TreeForeignKey
from taggit.managers import TaggableManager
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.image_warmer import VersatileImageFieldWarmer

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
        for i in range(0,len(body_parts)):
            if i%2 == 0: # skip even pieces because they're not surrounded by replace tokens
                continue
            cur_image = body_parts[i]
            if "|" in cur_image: # look for pipe delimiter for alt text embedded within the replace string
                img_name_pieces = cur_image.split("|")
                img_name = img_name_pieces[0]
                img_alt = img_name_pieces[1]
            else: # if it's not there, use the image name as alt text
                img_name = cur_image
                img_alt = cur_image
            try:
                img = Media.objects.get(image_name=img_name)
                if img.alt_text is None or (img.alt_text == img.image_name and img.alt_text != img_alt):
                    img.alt_text = img_alt
                    img.save()
                body_parts[i] = img.get_link_html()
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
            if "|" in img_name:
                img_name = img_name.split("|")[0]
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
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', db_index=True)
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
            prefix = '<a class="collapsible" href="#cat-%s">%s</a> &nbsp;' % (self.slug, prefix_character)
        return '<li>%s<a href="%s">%s</a></li>\n' % (prefix, self.get_absolute_url(), self.title)
    
    def get_active_string(self):
        if not self.active:
            return "collapse"
        return ""
        
class Media(models.Model):
    image_name = models.SlugField(max_length=200, unique=True)
    pub_date = models.DateTimeField('date published', default=timezone.now, editable=False)
    full_image = VersatileImageField(upload_to="full/%Y/%m/%d", max_length=400)
    scale_image = VersatileImageField(max_length=400, editable=False)
    alt_text = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "media"
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.image_name
        
    def get_blog_url(self):
        return "/blog/media/"+self.image_name
        
    def get_link_html(self):
        if self.full_image is None or self.scale_image is None:
            return '<img src="#" alt="Image not found" />'
        link_string = '<div class="text-center"><a href="%s"><img src="%s" height="%s" width="%s" class="img-fluid" alt="%s" /></a></div>'
        if self.alt_text is None:
            img_alt = self.image_name
        else:
            img_alt = self.alt_text
        return link_string % (self.full_image.url, self.scale_image.url, self.scale_image.height, self.scale_image.width, img_alt)
    
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
        
        
class Mapping(models.Model):
    source = models.URLField()
    dest = models.URLField()