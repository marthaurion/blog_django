import datetime, time

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView, DayArchiveView

from taggit.models import Tag

from .models import Post, Category, Media


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
    context_object_name = 'post_list'
    template_name = 'blog/post_index.html'


# display every published post
class PostIndexView(PostListMixin, ArchiveIndexView):
    model = Post
    date_field = 'pub_date'
    
    def get_context_data(self, **kwargs):
        context = super(PostIndexView, self).get_context_data(**kwargs)
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        title = "Marth's Anime Blog"
        if working_page > 1:
            title += ' - Page ' + str(working_page)
        
        context['page_title'] = title
        context['base_url'] = '/blog/'
        return context


# display all posts published in a given year
class PostYearView(PostListMixin, YearArchiveView):
    model = Post
    date_field = 'pub_date'
    make_object_list = True
    
    def get_context_data(self, **kwargs):
        context = super(PostYearView, self).get_context_data(**kwargs)
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
        return context


# display all posts published in a given month
class PostMonthView(PostListMixin, MonthArchiveView):
    model = Post
    date_field = 'pub_date'
    month_format = "%m"
    make_object_list = True
    
    def get_context_data(self, **kwargs):
        context = super(PostMonthView, self).get_context_data(**kwargs)
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
        return context


# display all posts published on a given day
class PostDayView(PostListMixin, DayArchiveView):
    model = Post
    date_field = 'pub_date'
    month_format = "%m"
    make_object_list = True
    
    def get_context_data(self, **kwargs):
        context = super(PostDayView, self).get_context_data(**kwargs)
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
        return context


# display all posts for a category
class CategoryListView(PostListMixin, ListView):
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        category_list = category.get_descendants(include_self=True)
        posts = Post.published.filter(category__in=category_list)
        return posts
        
    def get_context_data(self, **kwargs):
        context = super(CategoryListView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        category = Category.objects.get(slug=slug)
        title = "Posts for Category: " + category.title
        page_header = title
        if working_page > 1:
            title = title + " - Page " + str(working_page)
            
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/category/'+slug+'/'
        return context


# display all posts for a tag
class TagListView(PostListMixin, ListView):
    def get_queryset(self):
        posts = Post.published.filter(tags__slug__in=[self.kwargs['slug']])
        return posts
        
    def get_context_data(self, **kwargs):
        context = super(TagListView, self).get_context_data(**kwargs)
        slug = self.kwargs['slug']
        
        working_page = 1
        if 'page' in self.kwargs:
            working_page = int(self.kwargs['page'])
        
        tag = Tag.objects.get(slug=slug)
        title = "Posts for Tag: " + tag.name
        page_header = title
        if working_page > 1:
            title = title + " - Page " + str(working_page)
            
        context['page_title'] = title
        context['page_header'] = page_header
        context['base_url'] = '/blog/tag/'+slug+'/'
        
        return context


# display a single post
class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    month_format = "%m"
    
    # override get object so that it gives a 404 error if you're looking at a post in the future and you're not an admin
    def get_object(self, *args, **kwargs):
        obj = super(PostDetailView, self).get_object(*args, **kwargs)
        if obj.pub_date>timezone.now(): # don't show future posts
            if not self.request.user.is_active and not self.request.user.is_superuser: # only block if not an admin
                raise Http404()
        return obj


class SearchResultsView(PostListMixin, ListView):
    def get_queryset(self):
        query = self.request.GET.get('q')
        
        posts = Post.published.extra(
            select={'rank': "ts_rank_cd(to_tsvector('english', title || ' ' || body_html), plainto_tsquery(%s), 32)"},
            select_params=(query,),
            where=("to_tsvector('english', title || ' ' || body_html) @@ plainto_tsquery(%s)",),
            params=(query,),
            order_by=('-rank',)
        )
        #posts = Post.published.annotate(
            #search=SearchVector('title', 'body_html'),
        #).filter(search=query)
        return posts
        
    def get_context_data(self, **kwargs):
        context = super(SearchResultsView, self).get_context_data(**kwargs)
        
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