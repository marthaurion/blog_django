from django.contrib import sitemaps
from django.core.urlresolvers import reverse

from blog.models import Post

class BlogSitemap(sitemaps.Sitemap):
    changefreq = 'never'
    priority = 0.7

    def items(self):
        return Post.published.all()

    def lastmod(self, obj):
        return obj.pub_date


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'yearly'

    def items(self):
        return ['about', 'blogroll', 'contact']

    def location(self, item):
        return reverse(item)
        
class IndexSitemap(sitemaps.Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)