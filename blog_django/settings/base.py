"""
Django settings for blog_django project.

Generated by 'django-admin startproject' using Django 1.8.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import json
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

with open(os.path.join(os.path.dirname(BASE_DIR), "config.json")) as f:
    secrets = json.loads(f.read())

def get_secret(setting, secrets=secrets):
    try:
        return secrets[setting]
    except KeyError:
        error_msg = "Set the {0} environment variable".format(setting)
        raise ImproperlyConfigured(error_msg)

STATICFILES_DIRS = (
    os.path.join(os.path.dirname(BASE_DIR), "assets"),
)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secret("SECRET_KEY")
SITE_ID = 1

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'django.contrib.postgres',
    'captcha',
    'blog',
    'taggit',
    'storages',
    'disqus',
    'maintenancemode',
    'bulk_admin',
    'django.contrib.sitemaps',
    'versatileimagefield',
    'mptt',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'maintenancemode.middleware.MaintenanceModeMiddleware',
)

ROOT_URLCONF = 'blog_django.urls'

ALLOWED_HOSTS = ['.marthaurion.com', 'blank-django-marthaurion.c9users.io', 'www.codebecauseican.com' 'localhost']

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(os.path.dirname(BASE_DIR), "templates")],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'blog.context_processors.category_list',
            ],
        },
    },
]

DISQUS_WEBSITE_SHORTNAME = 'marthaurion'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'blog',
        'USER': get_secret("DATABASE_USER"),
        'PASSWORD': get_secret("DATABASE_PASS"),
        'HOST': get_secret("DATABASE_HOST"),
        'PORT': get_secret("DATABASE_PORT"),
    }
}

MAINTENANCE_MODE = False

MAINTENANCE_IGNORE_URLS = (
    r'^/admin/*',
)

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'America/Chicago'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

AWS_HEADERS = {
    'Expires': 'Thu, 31 Dec 2099 20:00:00 GMT',
    'Cache-Control': 'max-age=94608000',
}

AWS_STORAGE_BUCKET_NAME = 'marthblog'

AWS_ACCESS_KEY_ID = get_secret("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = get_secret("AWS_SECRET_ACCESS_KEY")

DISQUS_API_KEY = get_secret('DISQUS_API_KEY')

EMAIL_HOST_PASSWORD = get_secret('EMAIL_HOST_PASSWORD')

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'marthaurionblog@gmail.com'

VERSATILEIMAGEFIELD_SETTINGS = {
    'create_images_on_demand': False,
    'jpeg_resize_quality': 90,
}

VERSATILEIMAGEFIELD_RENDITION_KEY_SETS = {
    'first_image': [
        ('first_image_thumb', 'thumbnail__200x200'),
    ],
    'scaled_image': [
        ('scaled_image_thumb', 'thumbnail__750x540')
    ]
}