from .models import Category

def category_list(request):
    return {'categories': Category.objects.filter(parent__isnull=True)} 