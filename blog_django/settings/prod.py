from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

#AWS_CLOUDFRONT_DOMAIN = "d34zzkuru6phz2.cloudfront.net"
AWS_CLOUDFRONT_DOMAIN = "media.codebecauseican.com"

STATICFILES_LOCATION = 'static'
#STATIC_URL = "https://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, STATICFILES_LOCATION)
STATIC_URL = "http://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, STATICFILES_LOCATION)
STATICFILES_STORAGE = 'blog_django.custom_storages.StaticStorage'

MEDIAFILES_LOCATION = 'media'
#MEDIA_URL = "https://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, MEDIAFILES_LOCATION)
MEDIA_URL = "http://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'blog_django.custom_storages.MediaStorage'