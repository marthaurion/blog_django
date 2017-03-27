from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from blog.models import Post, Media

class BlogSitemap(sitemaps.Sitemap):
    changefreq = 'never'
    priority = 0.7
    protocol = 'https'

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.pub_date


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'
    protocol = 'https'

    def items(self):
        return ['about', 'blogroll', 'contact', 'reviews']

    def location(self, item):
        return reverse(item)
        
        
class IndexSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'daily'
    protocol = 'https'

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)
        
        
class MediaSitemap(sitemaps.Sitemap):
    priority = 0.7
    changefreq = 'never'
    protocol = 'https'
    
    def items(self):
        return Media.objects.all()
    
    def lastmod(self, obj):
        return obj.pub_date
    
    def location(self, item):
        return item.get_blog_url()