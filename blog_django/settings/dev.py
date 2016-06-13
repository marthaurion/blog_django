from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []

STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), "static")
STATIC_URL = '/static/'