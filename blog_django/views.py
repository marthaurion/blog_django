from django.shortcuts import render_to_response
from blog.models import Category

# Create your views here.
def about_page(request):
    return render_to_response('about.html',
                              { 'categories': Category.objects.filter(parent__isnull=True) })

def contact_page(request):
    return render_to_response('contact.html',
                              { 'categories': Category.objects.filter(parent__isnull=True) })