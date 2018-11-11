from django.urls import path, re_path, include

from .feeds import LatestEntriesFeed
from .views import PostDetailView, TagListView, CategoryListView, PostIndexView, PostYearView, PostMonthView, PostDayView, SearchResultsView, MediaDetailView


urlpatterns = [
    path('', PostIndexView.as_view()),
    path('feed/', LatestEntriesFeed()),
    path('results/', SearchResultsView.as_view(), name='blog_search_list'),
    path('media/<name>/', MediaDetailView.as_view()),
    re_path('page/(?P<page>\d+)/$', PostIndexView.as_view()),
    re_path('category/(?P<slug>[-\w]+)/$', CategoryListView.as_view()),
    re_path(r'^category/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', CategoryListView.as_view()),
    re_path(r'^tag/(?P<slug>[-\w]+)/$', TagListView.as_view()),
    re_path(r'^tag/(?P<slug>[-\w]+)/page/(?P<page>\d+)/$', TagListView.as_view()),
    re_path(r'^(?P<year>\d{4})/$', PostYearView.as_view()),
    re_path(r'^(?P<year>\d{4})/page/(?P<page>\d+)/$', PostYearView.as_view()),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/$', PostMonthView.as_view()),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/page/(?P<page>\d+)/$', PostMonthView.as_view()),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/$', PostDayView.as_view()),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/page/(?P<page>\d+)/$', PostDayView.as_view()),
    re_path(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-\w]+)/$', PostDetailView.as_view()),
]
