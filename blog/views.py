import datetime, time

from django.conf import settings
from django.contrib.postgres.search import SearchVector
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic.detail import DetailView
from django.views.generic.edit import FormMixin
from django.views.generic.list import ListView
from django.views.generic.dates import ArchiveIndexView, YearArchiveView, MonthArchiveView, DayArchiveView

from taggit.models import Tag

from .models import Post, Category, Media, Comment, Commenter
from .forms import CommentForm
from .tasks import send_email


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
        context = super().get_context_data(**kwargs)
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
        return context


# display all posts for a category
class CategoryListView(PostListMixin, ListView):
    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['slug'])
        category_list = category.get_descendants(include_self=True)
        posts = Post.published.filter(category__in=category_list)
        return posts
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        context = super().get_context_data(**kwargs)
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


class CommentFormMixin(FormMixin):
    form_class = CommentForm
    
    # override initial values for the form to use session values for a commenter if they exist
    def get_initial(self):
        return { 'username': self.request.session.get('comment_username'),
                'email': self.request.session.get('comment_email'),
                'website': self.request.session.get('comment_website') }

    def comment_check(self, request, form, post=None, page_url=None):
        form_email = form.cleaned_data['email']
        form_username = form.cleaned_data['username']
        form_website = form.cleaned_data['website']
        commenter = Commenter.objects.filter(email=form_email)
        if not commenter: # if no commenter is found for the email in the form, create one
            author = Commenter()
            author.email = form_email
            author.username = form_username
            author.website = form_website
            author.save()
        else: # if we find a commenter with the email, use it
            author = commenter[0]
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
        
        request.session['comment_email'] = author.email  # save commenter information in a session so it can be reused later
        request.session['comment_username'] = author.username
        request.session['comment_website'] = author.website
        
        comment = Comment()
        if form.cleaned_data['parent']:
            parent_id = int(form.cleaned_data['parent'].replace('#comment',''))
            comment.parent = Comment.objects.get(pk=parent_id)
        
        if post:
            comment.post = post # use the post attached to this view as the post for this comment
        else:
            comment.page_url = page_url
        comment.author = author
        if author.approved: # if the author is always approved, mark the comment as approved
            comment.approved = True
        comment.text = form.cleaned_data['text'] # pull from the form
        comment_notify = bool(request.POST.get('notify', False))
        comment.notify = comment_notify # if the checkbox is checked, set notify field
        if author.spam:
            comment.spam = True
        comment.save()
        
        request.session['comment_notify'] = comment_notify # log notification setting in the session
        
        request_info = comment.get_request_info(request)
        if settings.DEV_SERVER: # can't set up celery on cloud9, so running the standard email
            comment.send_notifications(request_info)
        else:
            send_email.delay(comment.pk, request_info)
        
        self.success_url = comment.get_absolute_url()
        return self.form_valid(form)


# display a single post
class PostDetailView(CommentFormMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    month_format = "%m"
    
    def get(self, request, *args, **kwargs):
        if 'email' in request.GET and 'comment' in request.GET:
            comment_pk = int(request.GET['comment'])
            comment = Comment.objects.filter(pk=comment_pk)
            if len(comment):
                comment[0].unsubscribe(request.GET['email'])
            
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
        context['comment_list'] = self.object.approved_comments()
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