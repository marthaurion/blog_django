from django.contrib import admin

from .models import Commenter, Comment


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
    
    mark_spam.short_description = "Mark the comments as spam"
    
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
            commenter.mark_spam()
    
    mark_spam.short_description = "Mark the users as spammers"
    
    def mark_not_spam(self, request, queryset):
        for commenter in queryset:
            commenter.mark_safe()
    
    mark_not_spam.short_description = "Mark the users as safe"