import datetime, time

from django.contrib.postgres.search import SearchVector
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from django.views.generic.dates import YearArchiveView, MonthArchiveView, DayArchiveView

import logging

from taggit.models import Tag
from rest_framework import viewsets
from .serializers import PostSerializer

from comments.views import CommentFormMixin
from .models import Post, Category, Media
from .helpers import PostPaginator


logger = logging.getLogger(__name__)\


class PostViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.
    """
    queryset = Post.published.all()
    serializer_class = PostSerializer


class MediaDetailView(DetailView):
    model = Media
    template_name = 'blog/image_detail.html'
    context_object_name = 'img'
        
    def get_object(self, *args, **kwargs):
        return get_object_or_404(Media, image_name=self.kwargs['name'])

# for some of the shared stuff in these views
class PostListMixin(object):
    paginate_by = 10
    allow_empty = True
    paginator_class = PostPaginator
    context_object_name = 'post_list'
    template_name = 'blog/post_index.html'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return self.build_post_queryset(queryset)
                                                
    def build_post_queryset(self, queryset):
        return queryset.defer('body', 'body_html').select_related('category')


# display every published post
class PostIndexView(PostListMixin, ListView):
    model = Post
    ordering = '-pub_date'
    
    def get_queryset(self):
        return Post.published.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        title = "Marth's Anime Blog"
        if working_page > 1:
            title += ' - Page ' + str(working_page)
        
        context['page_title'] = title
        context['base_url'] = '/blog/'
        context['post_list'] = self.build_post_queryset(context['post_list'])
        return context


# display all posts published in a given year
class PostYearView(PostListMixin, YearArchiveView):
    model = Post
    date_field = 'pub_date'
    make_object_list = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs['year']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        dt = datetime.datetime(int(year), 1, 1)
        title = "Posts from " + dt.strftime('%Y')
        page_header = title
        if working_page > 1:
            title += ' - Page ' + str(working_page)
        
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/'+year+'/'
        context['post_list'] = self.build_post_queryset(context['post_list'])
        return context


# display all posts published in a given month
class PostMonthView(PostListMixin, MonthArchiveView):
    model = Post
    date_field = 'pub_date'
    month_format = "%m"
    make_object_list = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs['year']
        month = self.kwargs['month']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        dt = datetime.datetime(int(year), int(month), 1)
        title = "Posts from " + dt.strftime('%B %Y')
        page_header = title
        if working_page > 1:
            title += ' - Page ' + str(working_page)
        
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/'+year+'/'+month+'/'
        context['post_list'] = self.build_post_queryset(context['post_list'])
        return context


# display all posts published on a given day
class PostDayView(PostListMixin, DayArchiveView):
    model = Post
    date_field = 'pub_date'
    month_format = "%m"
    make_object_list = True
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.kwargs['year']
        month = self.kwargs['month']
        day = self.kwargs['day']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        dt = datetime.datetime(int(year), int(month), int(day))
        title = "Posts from " + dt.strftime('%B %d, %Y')
        page_header = title
        if working_page > 1:
            title += ' - Page ' + str(working_page)
        
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/'+year+'/'+month+'/'+day+'/'
        context['post_list'] = self.build_post_queryset(context['post_list'])
        return context


# display all posts for a category
class CategoryListView(PostListMixin, ListView):
    post_category = None
    
    def get_queryset(self):
        self.post_category = get_object_or_404(Category, slug=self.kwargs['slug'])
        category_list = self.post_category.get_descendants(include_self=True)
        posts = Post.published.filter(category__in=category_list)
        return posts
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        category = self.post_category
        title = "Posts for Category: " + category.title
        page_header = title
        if working_page > 1:
            title = title + " - Page " + str(working_page)
            
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/category/'+slug+'/'
        context['post_list'] = self.build_post_queryset(context['post_list'])
        return context


# display all posts for a tag
class TagListView(PostListMixin, ListView):
    def get_queryset(self):
        posts = Post.published.filter(tags__slug__in=[self.kwargs['slug']])
        return posts
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs['slug']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        tag = get_object_or_404(Tag, slug=slug)
        title = "Posts for Tag: " + tag.name
        page_header = title
        if working_page > 1:
            title = title + " - Page " + str(working_page)
            
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/tag/'+slug+'/'
        context['post_list'] = self.build_post_queryset(context['post_list'])
        return context


# display a single post
class PostDetailView(CommentFormMixin, FormMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    month_format = "%m"
    
    def get(self, request, *args, **kwargs):
        if 'email' in request.GET and 'comment' in request.GET:
            self.unsubscribe_comment(request.GET['comment'], request.GET['email'])
        return super().get(request, *args, **kwargs)
    
    # override get object so that it gives a 404 error if you're looking at a post in the future and you're not an admin
    def get_object(self, *args, **kwargs):
        obj = super().get_object(*args, **kwargs)
        if obj.pub_date>timezone.now(): # don't show future posts
            if not self.request.user.is_active and not self.request.user.is_superuser: # only block if not an admin
                raise Http404()
        return obj
        
    # add comment notify to context from session
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_notify'] = self.request.session.get('comment_notify')
        context['comment_username'] = self.request.session.get('comment_username')
        if context['comment_username']:
            context['comment_hidden'] = ' hidden'
        else:
            context['comment_hidden'] = ''
        context['comment_list'] = self.object.approved_comments().select_related('author')
        context['post_comment_url'] = self.object.get_absolute_url()
        return context
        
    # override the post function to handle the form values and create a comment
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.comment_check(request, form, self.object)
        else:
            return self.form_invalid(form)


class SearchResultsView(PostListMixin, ListView):
    template_name = 'blog/search_index.html'
    
    def get_queryset(self):
        query = self.request.GET.get('q')
        
        posts = Post.published.extra(
            select={'rank': "ts_rank_cd(to_tsvector('english', title || ' ' || body_html), plainto_tsquery(%s), 32)"},
            select_params=(query,),
            where=("to_tsvector('english', title || ' ' || body_html) @@ plainto_tsquery(%s)",),
            params=(query,),
            order_by=('-rank',)
        )
        return posts
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        title = "Search Results"
        page_header = title
        if working_page > 1:
            title = title + " - Page " + str(working_page)
            
        context['page_title'] = title
        context['page_header'] = page_header
        context['search'] = True
        context['query'] = self.request.GET.get('q')
        return context