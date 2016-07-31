from django.db import models
from django.utils import timezone
from datetime import timedelta
from taggit.managers import TaggableManager
from django.utils.timezone import localtime

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

    objects = models.Manager()
    published = PostManager()

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        local_pub_date = localtime(self.pub_date)
        return "/blog/%s/%s/" % (local_pub_date.strftime("%Y/%m/%d"), self.slug)
        
    def get_full_url(self):
        return "<a href='%s'>%s</a>" % (self.get_absolute_url(), self.get_absolute_url())
    get_full_url.short_description = 'Link'
    get_full_url.allow_tags = True
        
    # override save so we can add the linked images to the post
    def save(self, *args, **kwargs):
        link_string = '<a href="%s"><img src="%s" height="%s" width="%s" class="img-responsive" /></a>'
        body_parts = self.body.split("{{REPLACE}}")
        for i in range(0,len(body_parts)):
            if i%2 == 0: # skip even pieces because they're not surrounded by replace tokens
                continue
            cur_image = body_parts[i]
            img_search = Media.objects.filter(image_name=cur_image)
            if img_search:
                img = img_search[0] # should be only one
                link_text = link_string % (img.full_image.url, img.scale_image.url, img.scale_image.height, img.scale_image.width)
                body_parts[i] = link_text
        self.body_html = "".join(body_parts)
        super(Post, self).save(*args, **kwargs)

class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title

    def get_descendants(self): # build a list of all descendants for a category
        children = []
        for child in self.category_set.all():
            children.append(child)
            grandchildren = child.get_descendants()
            for grandchild in grandchildren:
                children.append(grandchild)

        return children

    def get_absolute_url(self):
        return "/blog/category/%s/" % self.slug
        
        
class Media(models.Model):
    image_name = models.CharField(max_length=200, unique=True)
    pub_date = models.DateTimeField('date published', default=timezone.now, editable=False)
    full_image = models.ImageField(upload_to="full/%Y/%m/%d", max_length=200)
    scale_image = models.ImageField(upload_to="scale/%Y/%m/%d", max_length=200)
    
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