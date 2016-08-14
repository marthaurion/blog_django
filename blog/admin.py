from django.contrib import admin

from .models import Post, Category, Media
import bulk_admin

# Register your models here.

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    list_display = ('title', 'get_full_url', 'pub_date', 'admin_first_image', )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    
@admin.register(Media)
class MediaAdmin(bulk_admin.BulkModelAdmin):
    list_display = ('image_name', 'pub_date', 'admin_thumbnail', 'admin_full', )