from django.conf.urls import include, url
from . import views


urlpatterns = [
    url(r'^$', views.post_index),
    url(r'^page/(?P<page>\d+)/$', views.post_index),
    url(r'^category/(?P<slug>[-\w]+)/$', views.category_index),
    url(r'^category/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', views.category_index),
    url(r'^tag/(?P<slug>[-\w]+)/$', views.tag_index),
    url(r'^tag/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', views.tag_index),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', views.post_detail),
]
