from django.shortcuts import render, render_to_response
from .models import Post

# Create your views here.
def post_index(request):
    return render_to_response('blog/post_index.html',
                               { 'post_list': Post.objects.all() })