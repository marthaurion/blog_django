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
from django.urls import path, include
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import GenericSitemap
from django.contrib.sitemaps import views as sitemap_views
from django.views.generic.base import RedirectView

from captcha import urls as captcha_urls

from blog.views import PostIndexView
from blog import urls as blog_urls

from .sitemaps import StaticViewSitemap, BlogSitemap, IndexSitemap, MediaSitemap
from .views import AboutView, BlogrollView, ContactView, ReviewsView, CategoryRedirectView

sitemaps = {
    'home': IndexSitemap,
    'blog': BlogSitemap,
    'static': StaticViewSitemap,
    'media': MediaSitemap
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('blog/', include(blog_urls)),
    path('about/', AboutView.as_view(), name='about'),
    path('contact/', ContactView.as_view(), name='contact'),
    path('blogroll/', BlogrollView.as_view(), name='blogroll'),
    path('reviews/', ReviewsView.as_view(), name='reviews'),
    path('sitemap.xml', sitemap_views.index, {'sitemaps': sitemaps}),
    path('sitemap-<section>.xml', sitemap_views.sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('captcha/', include(captcha_urls)),
    path('tag/<url>/', RedirectView.as_view(url="/blog/tag/%(url)s", permanent=True)),  # some catch alls to reduce 404 errors
    path('page/<url>/', RedirectView.as_view(url="/blog/page/%(url)s", permanent=True)),
    path('<int:year>/', RedirectView.as_view(url="/blog/%(year)s", permanent=True)),
    path('<int:year>/<url>/', RedirectView.as_view(url="/blog/%(year)s/%(url)s", permanent=True)),
    path('category/<url>/page/<page>/', CategoryRedirectView.as_view()),
    path('category/<url>/', CategoryRedirectView.as_view()),
    path('', PostIndexView.as_view(), name='index'),
]

if settings.DEV_SERVER: # there is a debug mode for production, but it turns on maintenance mode
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    import debug_toolbar  # if we're on the dev server, include urls for debug toolbar
    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]