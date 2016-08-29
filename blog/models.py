from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from datetime import timedelta
from taggit.managers import TaggableManager
from django.utils.timezone import localtime
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.image_warmer import VersatileImageFieldWarmer
import markdown

# Create your models here.
class PostManager(models.Manager):
    def get_queryset(self):
        return super(PostManager, self).get_queryset().filter(pub_date__lte=timezone.now())

def default_start_time():
    now = timezone.now()
    start = now.replace(hour=21, minute=0, second=0, microsecond=0)
    return start if start > now else start + timedelta(days=1)

class Post(models.Model):
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique_for_date='pub_date')
    excerpt = models.TextField()
    body = models.TextField()
    body_html = models.TextField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', default=default_start_time)
    tags = TaggableManager()
    first_image = VersatileImageField(null=True, editable=False, max_length=200)

    objects = models.Manager()
    published = PostManager()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        local_pub_date = localtime(self.pub_date)
        return "/blog/%s/%s/" % (local_pub_date.strftime("%Y/%m/%d"), self.slug)
        
    # add a link to the blog post on the admin list display to make it easier to preview the post
    def get_full_url(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), self.get_absolute_url())
    get_full_url.short_description = 'Link'
    get_full_url.allow_tags = True
    
    def admin_first_image(self): # show the first image on the admin list so we can make sure it gets set
        if not self.first_image:
            return u'None'
        return u'<img src="%s" height="150" />' % (self.first_image.url)
        
    admin_first_image.short_description = 'First Image'
    admin_first_image.allow_tags = True
    
    # takes the text of the post and replaces the {{REPLACE}} strings with the proper image text
    def process_image_links(self, body_parts):
        link_string = '<a href="%s"><img src="%s" height="%s" width="%s" class="img-responsive" /></a>'
        for i in range(0,len(body_parts)):
            if i%2 == 0: # skip even pieces because they're not surrounded by replace tokens
                continue
            cur_image = body_parts[i]
            img_search = Media.objects.filter(image_name=cur_image)
            if img_search:
                img = img_search[0] # should be only one
                link_text = link_string % (img.full_image.url, img.scale_image.url, img.scale_image.height, img.scale_image.width)
                body_parts[i] = link_text
        return "".join(body_parts)
        
    # override save so we can add the linked images to the post
    def save(self, *args, **kwargs):
        body_parts = self.body.split("{{REPLACE}}")
        image_processed = self.process_image_links(body_parts)
        self.body_html = markdown.markdown(image_processed)
        first_img = self.get_first_image()
        if first_img:
            self.first_image = first_img.full_image
        
        super(Post, self).save(*args, **kwargs)

    # get the first image from the body text
    def get_first_image(self):
        body_parts = self.body.split("{{REPLACE}}", 2) # only split twice because we're getting the first image, which is the second piece
        if len(body_parts) > 1:
            img_name = body_parts[1]
            img_search = Media.objects.filter(image_name=img_name) # find the image model
            if img_search:
                return img_search[0] # should be only one
        return None
        
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
    

class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['slug']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title

     # build a list of all descendants for a category
    def get_descendants(self):
        children = []
        for child in self.category_set.all():
            children.append(child)
            grandchildren = child.get_descendants()
            for grandchild in grandchildren:
                children.append(grandchild)

        return children

    def get_absolute_url(self):
        return "/blog/category/%s/" % self.slug
    
    # returns the html for this category and all sub-categories to display
    def display_category(self):
        children = self.category_set.all()
        if self.active:
            active_string = " in"
            prefix_character = "&#9660;"
        else:
            active_string = ""
            prefix_character = "&#9658;"
        
        if children:
            prefix = '<span class="list-prefix"><a class="collapsible" href="#%s" data-toggle="collapse">%s</a> &nbsp;</span>' % (self.slug, prefix_character)
        else:
            prefix = '<span class="list-prefix">&#8212; &nbsp;</span>'
        
        html_string = '<li>%s<a href="%s">%s</a></li>\n' % (prefix, self.get_absolute_url(), self.title)
        if children:
            html_string += '<ul id="%s" class="list-unstyled collapse%s">\n' % (self.slug, active_string)
            
            for child in children:
                html_string += child.display_category()
            html_string += '</ul>\n'
        return html_string
        
class Media(models.Model):
    image_name = models.CharField(max_length=200, unique=True)
    pub_date = models.DateTimeField('date published', default=timezone.now, editable=False)
    full_image = VersatileImageField(upload_to="full/%Y/%m/%d", max_length=200)
    scale_image = VersatileImageField(upload_to="scale/%Y/%m/%d", max_length=200)
    
    class Meta:
        verbose_name_plural = "media"
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.image_name
    
    # this stuff is to show a preview of the image in the admin list
    def admin_thumbnail(self):
        return u'<img src="%s" height="150" />' % (self.scale_image.url)
        
    admin_thumbnail.short_description = 'Image'
    admin_thumbnail.allow_tags = True
    
    def admin_full(self):
        return u'<img src="%s" height="150" />' % (self.full_image.url)
        
    admin_full.short_description = 'Full Image'
    admin_full.allow_tags = True
    
    
def populate_first_image():
    for post in Post.published.all():
        first = post.get_first_image()
        if first:
            post.first_image = first
            post.save()