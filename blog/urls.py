from django.conf.urls import include, url


urlpatterns = [
    url(r'^$', 'blog.views.post_index'),
    url(r'^page/(?P<page>\d+)/$', 'blog.views.post_index'),
    url(r'^category/(?P<slug>[-\w]+)/$', 'blog.views.category_index'),
    url(r'^category/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', 'blog.views.category_index'),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', 'blog.views.post_detail'),
]
