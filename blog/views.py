import datetime, time

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from django.views.generic.dates import YearArchiveView, MonthArchiveView, DayArchiveView
from django.db import models

import logging

from taggit.models import Tag
from rest_framework import viewsets
from .serializers import PostSerializer

from .models import Post, Category, Media, Comment, Commenter
from .forms import CommentForm
from .tasks import send_email
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


class CommentFormMixin(object):
    form_class = CommentForm
    
    # override initial values for the form to use session values for a commenter if they exist
    def get_initial(self):
        return { 'username': self.request.session.get('comment_username'),
                'email': self.request.session.get('comment_email'),
                'website': self.request.session.get('comment_website') }

    def comment_check(self, request, form, post=None, page_url=''):
        form_email = form.cleaned_data['email']
        form_username = form.cleaned_data['username']
        form_website = form.cleaned_data['website']
        try:
            author = Commenter.objects.get(email=form_email)
            changed = False
            # if username or website are changed, update them for the author of the comment
            if form_website and form_website != author.website:
                author.website = form_website
                changed = True
            if form_username and form_username != author.username:
                author.username = form_username
                changed = True
            if changed:
                author.save()
        except Commenter.DoesNotExist: # if no commenter is found for the email in the form, create one
            author = Commenter()
            author.email = form_email
            author.username = form_username
            author.website = form_website
            author.save()
        except Commenter.MultipleObjectsReturned: # probably shouldn't happen, but here just in case
            logger.error('Multiple commenters found for email: %s' % form_email)
            return self.form_invalid(form)
        
        request.session['comment_email'] = author.email  # save commenter information in a session so it can be reused later
        request.session['comment_username'] = author.username
        request.session['comment_website'] = author.website
        
        # prep comment fields before creating the new comment
        parent = None
        if form.cleaned_data['parent']:
            parent_id = form.cleaned_data['parent'].replace('#comment','')
            try:
                parent = Comment.objects.get(uuid=parent_id)
            except (Comment.MultipleObjectsReturned, Comment.DoesNotExist):
                logger.error('Invalid parent comment id: %d' % parent_id)
        comment_notify = bool(request.POST.get('notify', False))
        
        search_time = timezone.now()-datetime.timedelta(seconds=10)
        # try to find the same comment in the last 10 seconds or create a new one otherwise
        comment, created = Comment.objects.get_or_create(
            parent=parent,
            post=post, # this will be None if it's a page
            page_url=page_url, # this will be an empty string if it's a post
            pub_date__gt=search_time,
            text=form.cleaned_data['text'],
            author=author,
            approved=author.approved,
            notify=comment_notify,
            spam=author.spam
        )
        self.success_url = comment.get_absolute_url()
        if not created: # if this is a duplicate, return without notification
            return self.form_valid(form)
        
        request.session['comment_notify'] = comment_notify # log notification setting in the session
        
        request_info = comment.get_request_info(request)
        if settings.DEV_SERVER: # can't set up celery on cloud9, so running the standard email
            comment.send_notifications(request_info)
        else:
            send_email.delay(comment.pk, request_info)
        return self.form_valid(form)
        
    def unsubscribe_comment(self, uuid, email):
        try:
            comment = Comment.objects.get(uuid=uuid)
            comment.unsubscribe(email)
        except (Comment.MultipleObjectsReturned, Comment.DoesNotExist):
            logger.error('Email unsubscribe failed for comment: %d' % uuid)


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