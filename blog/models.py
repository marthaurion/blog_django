from django.db import models
import datetime

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique_for_date='pub_date')
    excerpt = models.CharField(max_length=200)
    body = models.TextField()
    category = models.ForeignKey('Category')
    pub_date = models.DateTimeField('date published', default=datetime.datetime.now)
    
    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return "/blog/%s/%s/" % (self.pub_date.strftime("%Y/%m/%d"), self.slug)

class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    parent = models.ForeignKey('self', null=True, blank=True)
    
    class Meta:
        ordering = ['title']
        verbose_name_plural = "categories"
        
    def __str__(self):
        return self.title
        
    def get_absolute_url(self):
        return "/blog/category/%s/" % self.slug