from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
INSTALLED_APPS += ('debug_toolbar', )

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static")
STATIC_URL = '/static/'

MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR), "media")
MEDIA_URL = '/media/'