import datetime, time

from django.shortcuts import get_object_or_404, render
from django.http import Http404
from django.core.paginator import Paginator
from django.utils import timezone
from taggit.models import Tag
from .models import Post, Category

# experimental imports
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic.detail import DetailView

POSTSPERPAGE = 7

# Create your views here.
# each of the index views has a slightly different filter function, so I split them out

# all
def post_index(request, page=1):
    posts = Post.published.all()
    return post_index_helper(request, page, posts)

# by year
def post_index_year(request, year, page=1):
    posts = Post.published.filter(pub_date__year=year)
    dt = datetime.datetime(int(year), 1, 1)
    title_string = "Posts from " + dt.strftime('%Y')
    base_url = '/blog/'+year+'/'
    return post_index_helper(request, page, posts, title_string, base_url)
    
# by month
def post_index_month(request, year, month, page=1):
    posts = Post.published.filter(pub_date__year=year,
                                pub_date__month=month)
    dt = datetime.datetime(int(year), int(month), 1)
    title_string = "Posts from " + dt.strftime('%B %Y')
    base_url = '/blog/'+year+'/'+month+'/'
    return post_index_helper(request, page, posts, title_string, base_url)
    
# by day
def post_index_day(request, year, month, day, page=1):
    posts = Post.published.filter(pub_date__year=year,
                                pub_date__month=month,
                                pub_date__day=day)
    dt = datetime.datetime(int(year), int(month), int(day))
    title_string = "Posts from " + dt.strftime('%B %d, %Y')
    base_url = '/blog/'+year+'/'+month+'/'+day+'/'
    return post_index_helper(request, page, posts, title_string, base_url)

# shared code for all of the index calls
def post_index_helper(request, page, posts, title=None, base_url=None):
    paginator = Paginator(posts, POSTSPERPAGE)
    
    page = int(page)
    if page < 1:
        page = 1
    elif page > paginator.num_pages:
        page = paginator.num_pages
    
    page_header = None
    if title is None:
        title = "Marth's Anime Blog"
        if page > 1:
            title += " - Page " + str(page)
    else:
        page_header = title
        if page > 1:
            title = title + " - Page " + str(page)
    
    if base_url is None:
        base_url = '/blog/'
    
    return render(request, 'blog/post_index.html',
                    { 'post_list': paginator.page(page),
                    'page_title': title, 'page_header': page_header,
                    'base_url': base_url })

# display posts by category
def category_index(request, slug, page=1):
    category = Category.objects.get(slug=slug)
    category_list = category.get_descendants()
    category_list.append(category)
    posts = Post.published.filter(category__in=category_list)
    
    paginator = Paginator(posts, POSTSPERPAGE)
    
    page = int(page)
    if page < 1:
        page = 1
    elif page > paginator.num_pages:
        page = paginator.num_pages
    
    
    page_header = "Posts for Category: " + category.title
    title = page_header
    if page > 1:
        title = title + " - Page " + str(page)
    
    return render(request, 'blog/post_index.html',
                    { 'post_list': paginator.page(page),
                    'page_title': title, 'page_header': page_header,
                    'base_url': '/blog/category/'+slug+'/' })

# display posts by tag
def tag_index(request, slug, page=1):
    tag = Tag.objects.get(slug=slug)
    posts = Post.published.filter(tags__in=[tag])
    
    paginator = Paginator(posts, POSTSPERPAGE)
    
    page = int(page)
    if page < 1:
        page = 1
    elif page > paginator.num_pages:
        page = paginator.num_pages
    
    title = "Posts for Tag: " + tag.name
    if page > 1:
        title = title + " - Page " + str(page)
    
    return render(request, 'blog/post_index.html',
                    { 'post_list': paginator.page(page),
                    'page_title': title, 'page_header': title,
                    'base_url': '/blog/tag/'+slug+'/' })
                    

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