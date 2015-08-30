from django.conf.urls import include, url

urlpatterns = [
    url(r'$', 'blog.views.post_index'),
]
