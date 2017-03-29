from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

INSTALLED_APPS += (
    'raven.contrib.django.raven_compat',
)

AWS_CLOUDFRONT_DOMAIN = "d34zzkuru6phz2.cloudfront.net"

STATICFILES_LOCATION = 'static'
STATIC_URL = "https://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, STATICFILES_LOCATION)
STATICFILES_STORAGE = 'blog_django.custom_storages.StaticStorage'

MEDIAFILES_LOCATION = 'media'
MEDIA_URL = "https://%s/%s/" % (AWS_CLOUDFRONT_DOMAIN, MEDIAFILES_LOCATION)
DEFAULT_FILE_STORAGE = 'blog_django.custom_storages.MediaStorage'

CELERY_BROKER_URL = get_secret("BROKER_URL")