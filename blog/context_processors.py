from .models import Category, Comment

def category_list(request):
    return { 'categories': Category.objects.all() }
    
def recent_comments(request):
    comment_set = Comment.objects.filter(approved=True, post__isnull=False).select_related('post', 'author').order_by('-pub_date')[:5]
    return { 'recent_comments': comment_set }