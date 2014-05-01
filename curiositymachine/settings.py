"""
Django settings for curiositymachine project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import dj_database_url

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

def process_false_string(value): # returns false on false-y values or 'false' string, true otherwise
    try:
        if not value or value.lower() == 'false':
            return False
        else:
            return True
    except AttributeError:
        return True

DEBUG = process_false_string(os.environ.get('DEBUG', False)) # debug saves a LOT of info and should never be left on in production

TEMPLATE_DEBUG = DEBUG

SITE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, "curiositymachine", "templates"),
)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY = os.getenv("SECRET_KEY", '0!)smlfbaj=4w7a=@#%5_5h*+n38m2c165xpbn9^#z_a%kgwrs')

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", '').split(',') if os.getenv("ALLOWED_HOSTS") else []

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'curiositymachine',
    'profiles',
    'challenges',
    'cmcomments',
    'videos',
    'images',
    'django_rq',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    "curiositymachine.context_processors.login_and_join_forms",
)

AUTH_USER_MODEL = 'auth.User'

ROOT_URLCONF = 'curiositymachine.urls'

WSGI_APPLICATION = 'curiositymachine.wsgi.application'

LOGIN_URL = '/login/'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases

DATABASES = {
    "default": dj_database_url.config(default='sqlite:///db.sqlite3'),
}

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = "America/Los_Angeles"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/

STATIC_URL = '/static/'

STATIC_ROOT = 'staticfiles'

FILEPICKER_API_KEY = os.getenv("FILEPICKER_API_KEY", "")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "curiositymachine")

ZENCODER_API_KEY = os.environ.get("ZENCODER_API_KEY", "")

S3_URL_BASE = "http://s3.amazonaws.com"

#job queues
RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
        'DB': 0,}
}

# Import optional local settings.  This must be at the END of this file.
try:
    from .local import *
except ImportError:
    pass
