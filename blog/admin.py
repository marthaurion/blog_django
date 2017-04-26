from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html
from django.conf.urls import url
from django import forms
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from mptt.admin import MPTTModelAdmin

from .models import Post, Category, Media
from .forms import BulkMediaForm

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    search_fields = ['title']
    list_display = ('title', 'get_full_url', 'wordpress_action', 'pub_date', 'admin_first_image', )
    
    # add a link to the blog post on the admin list display to make it easier to preview the post
    def get_full_url(self, instance):
        return "<a href='%s'>%s</a>" % (instance.get_absolute_url(), instance.get_absolute_url())
    get_full_url.short_description = 'Link'
    get_full_url.allow_tags = True
    
    # show the first image on the admin list so we can make sure it gets set
    def admin_first_image(self, instance):
        if not instance.first_image:
            return u'None'
        return u'<img src="%s" height="150" />' % (instance.first_image.url)
        
    admin_first_image.short_description = 'First Image'
    admin_first_image.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<post_id>.+)/wordpress/$',
                self.admin_site.admin_view(self.process_wordpress),
                name='post_wordpress',
            ),
        ]
        return custom_urls + urls
        
    def process_wordpress(self, request, post_id):
        post = self.get_object(request, post_id)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['post'] = post
        return TemplateResponse(request, 'admin/blog/wordpress.html', context)
        
    def wordpress_action(self, obj):
        return format_html(
            '<a class="button" href="{}">View</a>',
            reverse('admin:post_wordpress', args=[obj.pk])
        )
    wordpress_action.short_description = 'Wordpress'
    wordpress_action.allow_tags = True


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    search_fields = ['image_name']
    list_display = ('image_name', 'pub_date', 'admin_url', 'admin_thumbnail', 'admin_full', )
    change_list_template = 'admin/blog/bulk_upload_list.html'

    def generate_data_for_file(self, request, field_name, field_file, index):
        if field_name == 'full_image':
            index_string = '{0:02d}'.format(index+1)
            return dict(image_name=index_string)
    
    def admin_url(self, instance):
        return "<a href='%s'>%s</a>" % (instance.get_blog_url(), instance.get_blog_url())
        
    admin_url.short_description = 'Image URL'
    admin_url.allow_tags = True
    
    # this stuff is to show a preview of the image in the admin list
    def admin_thumbnail(self, instance):
        if not instance.scale_image:
            return u'None'
        return u'<img src="%s" height="150" />' % (instance.scale_image.url)
        
    admin_thumbnail.short_description = 'Image'
    admin_thumbnail.allow_tags = True
    
    def admin_full(self, instance):
        return u'<img src="%s" height="150" />' % (instance.full_image.url)
        
    admin_full.short_description = 'Full Image'
    admin_full.allow_tags = True
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^bulk-upload/$',
                self.admin_site.admin_view(self.process_bulk_upload),
                name='bulk_upload',
            ),
        ]
        return custom_urls + urls
    
    def process_bulk_upload(self, request, *args, **kwargs):
        if request.method != 'POST':
            form = BulkMediaForm()
        else:
            form = BulkMediaForm(request.POST, request.FILES)
            if form.is_valid():
                counter = 0
                base_name = form.cleaned_data['name']
                for img in request.FILES.getlist('images'):
                    counter += 1
                    new_med = Media()
                    new_med.image_name = base_name + '-{0:02d}'.format(counter)
                    new_med.full_image = img
                    new_med.save()
                self.message_user(request, "Success")
            else:
                self.message_user(request, "Error occurred")
            url = reverse(
                'admin:blog_media_changelist',
                current_app=self.admin_site.name,
            )
            return HttpResponseRedirect(url)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        return TemplateResponse(
            request,
            'admin/blog/bulk_upload.html',
            context,
        )