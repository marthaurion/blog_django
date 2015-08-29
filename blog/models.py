from django.db import models

# Create your models here.
class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    excerpt = models.CharField(max_length=200)
    body = models.TextField()
    category = models.ForeignKey('Category')
    pub_date = models.DateTimeField('date published')
    
    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.title

class Category(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField()
    parent = models.ForeignKey('self', null=True, blank=True)
    
    class Meta:
        ordering = ['title']
        verbose_name_plural = "categories"
        
    def __str__(self):
        return self.title