from django.contrib import admin

from .models import Post, Category, Media

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    
class MediaAdmin(admin.ModelAdmin):
    pass
    
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Media, MediaAdmin)