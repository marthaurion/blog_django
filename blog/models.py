from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from django.utils.timezone import localtime

# Create your models here.
class Media(models.Model):
    full_image = models.ImageField(upload_to="full/%Y/%m/%d", max_length=200, null=True, blank=True)
    scale_image = models.ImageField(upload_to="scale/%Y/%m/%d", max_length=200, null=True, blank=True)
    post_order = models.IntegerField()
    
    def __str__(self):
        return self.full_image.name
        
    class Meta:
        verbose_name_plural = "media"
        ordering = ['post_order']
        
class PostManager(models.Manager):
    def get_queryset(self):
        return super(PostManager, self).get_queryset().filter(pub_date__lte=timezone.now())

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='pub_date')
    excerpt = models.CharField(max_length=200)
    body = models.TextField()
    body_html = models.TextField(null=True, blank=True)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', default=timezone.now)
    media = models.ManyToManyField(Media)
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
        
    # override save so we can add the linked images to the post
    def save(self, *args, **kwargs):
        if self.pk is not None: # only try to do this if the values have changed because the media links won't work without a pk
            new_body = self.body
            linked_media = self.media.all()
            for m in linked_media:
                link_text = '<a href="%s"><img src="%s" height="%s" width="%s" class="img-responsive" /></a>' % (m.full_image.url, m.scale_image.url, m.scale_image.height, m.scale_image.width)
                new_body = new_body.replace("{{REPLACE}}", link_text, 1)
            self.body_html = new_body
        super(Post, self).save(*args, **kwargs)

class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['title']
        verbose_name_plural = "categories"

    def __str__(self):
        return self.title

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