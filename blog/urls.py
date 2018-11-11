from django.urls import path, include

from .feeds import LatestEntriesFeed
from .views import PostDetailView, TagListView, CategoryListView, PostIndexView, PostYearView, PostMonthView, PostDayView, SearchResultsView, MediaDetailView


urlpatterns = [
    path('', PostIndexView.as_view()),
    path('feed/', LatestEntriesFeed()),
    path('results/', SearchResultsView.as_view(), name='blog_search_list'),
    path('media/<name>/', MediaDetailView.as_view()),
    path('page/<int:page>/', PostIndexView.as_view()),
    path('category/<slug:slug>/', CategoryListView.as_view()),
    path('category/<slug:slug>/page/<int:page>/', CategoryListView.as_view()),
    path('tag/<slug:slug>/', TagListView.as_view()),
    path('tag/<slug:slug>/page/<int:page>/', TagListView.as_view()),
    path('<int:year>/', PostYearView.as_view()),
    path('<int:year>/page/<int:page>/', PostYearView.as_view()),
    path('<int:year>/<int:month>/', PostMonthView.as_view()),
    path('<int:year>/<int:month>/page/<int:page>/', PostMonthView.as_view()),
    path('<int:year>/<int:month>/<int:day>/', PostDayView.as_view()),
    path('<int:year>/<int:month>/<int:day>/page/<int:page>/', PostDayView.as_view()),
    path('<int:year>/<int:month>/<int:day>/<slug:slug>/', PostDetailView.as_view()),
]
