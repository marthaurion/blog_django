from django.contrib import admin

from bulk_admin import BulkModelAdmin
from mptt.admin import MPTTModelAdmin

from .models import Post, Category, Media, Link, Comment, Commenter, WordpressPost

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    search_fields = ['title']
    list_display = ('title', 'get_full_url', 'get_wordpress_url', 'pub_date', 'admin_first_image')
    
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
    
    # add a link to open the wordpress admin page
    def get_wordpress_url(self, instance):
        return "<a href='/admin/blog/wordpresspost/%d/change/'>/admin/blog/wordpresspost/%d/change/</a>" % (instance.id, instance.id) 
        
    get_wordpress_url.short_description = 'Wordpress'
    get_wordpress_url.allow_tags = True


@admin.register(WordpressPost)
class WordpressAdmin(PostAdmin):
    prepopulated_fields = {}
    fields = ('title', 'wordpress_body')
    list_display = ('title', 'get_full_url', 'pub_date', 'admin_first_image', )
    readonly_fields = ('title', 'wordpress_body')


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


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'pub_date', 'text', 'approved', 'notify', 'spam')
    list_filter = ['approved', 'spam']
    search_fields = ['author']
    actions = ['mark_approved', 'mark_not_approved', 'mark_spam', 'mark_not_spam']
    ordering = ['-pub_date']
    
    def mark_approved(self, request, queryset):
        for comment in queryset:
            comment.approve()
    
    mark_approved.short_description = "Approve the selected comments"
    
    def mark_not_approved(self, request, queryset):
        for comment in queryset:
            comment.unapprove()
    
    mark_not_approved.short_description = "Unapprove the selected comments"

    def mark_spam(self, request, queryset):
        for comment in queryset:
            comment.spam = True
            comment.save()
    
    mark_spam.short_description = "Mark the comments as spammers"
    
    def mark_not_spam(self, request, queryset):
        for comment in queryset:
            comment.spam = False
            comment.save()
    
    mark_not_spam.short_description = "Mark the comments as safe"


@admin.register(Commenter)
class CommenterAdmin(admin.ModelAdmin):
    list_display = ('username', 'approved', 'spam')
    list_filter = ['approved', 'spam']
    search_fields = ['username']
    actions = ['mark_approved', 'mark_not_approved', 'mark_spam', 'mark_not_spam']
    
    def mark_approved(self, request, queryset):
        for commenter in queryset:
            commenter.approve()
    
    mark_approved.short_description = "Approve the selected users"
    
    def mark_not_approved(self, request, queryset):
        for commenter in queryset:
            commenter.unapprove()
    
    mark_not_approved.short_description = "Unapprove the selected users"
    
    def mark_spam(self, request, queryset):
        for commenter in queryset:
            commenter.spam = True
            commenter.save()
    
    mark_spam.short_description = "Mark the users as spammers"
    
    def mark_not_spam(self, request, queryset):
        for commenter in queryset:
            commenter.spam = False
            commenter.save()
    
    mark_not_spam.short_description = "Mark the users as safe"