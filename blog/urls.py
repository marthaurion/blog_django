from django.conf.urls import include, url

from .feeds import LatestEntriesFeed
from .views import PostDetailView, TagListView, CategoryListView, PostIndexView, PostYearView, PostMonthView, PostDayView, SearchResultsView, MediaRedirectView


urlpatterns = [
    url(r'^$', PostIndexView.as_view()),
    url(r'^feed/$', LatestEntriesFeed()),
    url(r'^results/$', SearchResultsView.as_view(), name='blog_search_list'),
    url(r'^media/(?P<name>[-\w]+)/$', MediaRedirectView.as_view()),
    url(r'^page/(?P<page>\d+)/$', PostIndexView.as_view()),
    url(r'^category/(?P<slug>[-\w]+)/$', CategoryListView.as_view()),
    url(r'^category/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', CategoryListView.as_view()),
    url(r'^tag/(?P<slug>[-\w]+)/$', TagListView.as_view()),
    url(r'^tag/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', TagListView.as_view()),
    url(r'^(?P<year>\d{4})/$', PostYearView.as_view()),
    url(r'^(?P<year>\d{4})/page/(?P<page>\d+)/$', PostYearView.as_view()),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', PostMonthView.as_view()),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)/$', PostMonthView.as_view()),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', PostDayView.as_view()),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/page/(?P<page>\d+)/$', PostDayView.as_view()),
    url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', PostDetailView.as_view()),
]
