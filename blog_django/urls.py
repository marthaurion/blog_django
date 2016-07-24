"""blog_django URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps import views as sitemap_views
from . import views
from .sitemaps import StaticViewSitemap, BlogSitemap, IndexSitemap
from blog import views as blog_views


sitemaps = {
    'home': IndexSitemap,
    'blog': BlogSitemap,
    'static': StaticViewSitemap
}

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^blog/', include('blog.urls')),
    url(r'^about/$', views.about_page, name='about'),
    url(r'^contact/$', views.contact_page, name='contact'),
    url(r'^blogroll/$', views.blogroll_page, name='blogroll'),
    url(r'^messagereceived/$', views.contact_success, name='thanks'),
    url(r'^sitemap\.xml$', sitemap_views.index, {'sitemaps': sitemaps}),
    url(r'^sitemap-(?P<section>.+)\.xml$', sitemap_views.sitemap, {'sitemaps': sitemaps}),
    url(r'^$', blog_views.post_index, name='index'),
]

if settings.DEBUG and not settings.MAINTENANCE_MODE: # there is a debug mode for production, but it turns on maintenance mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)