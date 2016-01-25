from django.db import models
from django.utils import timezone
from taggit.managers import TaggableManager
from django.utils.timezone import localtime

# Create your models here.
class PostManager(models.Manager):
    def get_queryset(self):
        return super(PostManager, self).get_queryset().filter(pub_date__lte=timezone.now())

class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='pub_date')
    excerpt = models.CharField(max_length=200)
    body = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.CASCADE)
    pub_date = models.DateTimeField('date published', default=timezone.now)
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
            temp = child.get_descendants()
            if len(temp) > 0:
                children.append(temp)

        return children

    def get_absolute_url(self):
        return "/blog/category/%s/" % self.slug


class Media(models.Model):
    pub_date = models.DateTimeField('date published', default=timezone.now)
    full_image = models.ImageField(upload_to="full/%Y/%m/%d")
    post_image = models.ImageField(upload_to="posts/%Y/%m/%d")
    thumb = models.ImageField(upload_to="thumbs/%Y/%m/%d")

    class Meta:
        ordering = ['-pub_date']
        verbose_name_plural = "media"

    def __str__(self):
        return self.image.name
