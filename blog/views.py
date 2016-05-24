from django.shortcuts import get_object_or_404, render_to_response
from django.core.paginator import Paginator
from taggit.models import Tag
from .models import Post, Category

POSTSPERPAGE = 4

# Create your views here.
def post_index(request, page=1):
    posts = Post.published.all()
    return post_index_helper(request, page, posts)

def post_index_year(request, year, page=1):
    posts = Post.published.filter(pub_date__year=year)
    return post_index_helper(request, page, posts)
    
def post_index_month(request, year, month, page=1):
    posts = Post.published.filter(pub_date__year=year,
                                pub_date__month=month)
    return post_index_helper(request, page, posts)
    
def post_index_day(request, year, month, day, page=1):
    posts = Post.published.filter(pub_date__year=year,
                                pub_date__month=month,
                                pub_date__day=day)
    return post_index_helper(request, page, posts)

def post_index_helper(request, page, posts): # shared code for all of the index calls
    paginator = Paginator(posts, POSTSPERPAGE)
    
    page = int(page)
    if page < 1:
        page = 1
    elif page > paginator.num_pages:
        page = paginator.num_pages
    
    return render_to_response('blog/post_index.html',
                               { 'post_list': paginator.page(page),
                                 'categories': Category.objects.filter(parent__isnull=True) })

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
    
    return render_to_response('blog/post_index.html',
                               { 'post_list': paginator.page(page),
                                 'categories': Category.objects.filter(parent__isnull=True) })

def tag_index(request, slug, page=1):
    tag = Tag.objects.get(slug=slug)
    posts = Post.published.filter(tags__in=[tag])
    
    paginator = Paginator(posts, POSTSPERPAGE)
    
    page = int(page)
    if page < 1:
        page = 1
    elif page > paginator.num_pages:
        page = paginator.num_pages
    
    return render_to_response('blog/post_index.html',
                               { 'post_list': paginator.page(page),
                                 'categories': Category.objects.filter(parent__isnull=True) })
                                 
def post_detail(request, year, month, day, slug):
    import datetime, time
    from django.utils import timezone
    date_stamp = time.strptime(year+month+day, "%Y%m%d")
    pub_date = datetime.date(*date_stamp[:3])
    post = get_object_or_404(Post, pub_date__year=pub_date.year,
                                   pub_date__month=pub_date.month,
                                   pub_date__day=pub_date.day,
                                   slug=slug)
    if post.pub_date>timezone.now():
        raise Http404()
    return render_to_response('blog/post_detail.html',
                                { 'post': post,
                                  'categories': Category.objects.filter(parent__isnull=True) })