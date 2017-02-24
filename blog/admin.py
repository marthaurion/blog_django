from django.contrib import admin

from bulk_admin import BulkModelAdmin
from mptt.admin import MPTTModelAdmin

from .models import Post, Category, Media, Link

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    search_fields = ['title']
    list_display = ('title', 'get_full_url', 'pub_date', 'admin_first_image', )
    readonly_fields = ('body_html', )
    
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


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }


@admin.register(Media)
class MediaAdmin(BulkModelAdmin):
    search_fields = ['image_name']
    list_display = ('image_name', 'pub_date', 'admin_url', 'admin_thumbnail', 'admin_full', )
    
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
    
    
@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    pass