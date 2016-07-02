from django.contrib import admin

from .models import Post, Category, Media
import bulk_admin

# Register your models here.
class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    list_display = ('title', 'get_full_url', 'pub_date', )

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = { 'slug': ['title'] }
    
class MediaAdmin(bulk_admin.BulkModelAdmin):
    list_display = ('image_name', 'pub_date', 'admin_thumbnail', )
    
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Media, MediaAdmin)