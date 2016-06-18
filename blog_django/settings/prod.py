from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

STATICFILES_STORAGE = 'blog_django.custom_storages.StaticStorage'
STATIC_URL = "http://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, STATICFILES_LOCATION)

MEDIA_URL = "http://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'blog_django.custom_storages.MediaStorage'