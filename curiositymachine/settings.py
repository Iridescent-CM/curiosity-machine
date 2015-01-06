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

COMPRESS_ENABLED = process_false_string(os.environ.get('COMPRESS_ENABLED', False)) # no compression by default for now

ADMINS = tuple([("Curiosity Machine Admin", email) for email in os.getenv("ADMINS", '').split(',')])

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = SECRET_KEY = os.getenv("SECRET_KEY", '0!)smlfbaj=4w7a=@#%5_5h*+n38m2c165xpbn9^#z_a%kgwrs')

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", '').split(',') if os.getenv("ALLOWED_HOSTS") else []
MENTOR_RELATIONSHIP_MANAGERS = os.getenv("MENTOR_RELATIONSHIP_MANAGERS", '').split(',') if os.getenv("MENTOR_RELATIONSHIP_MANAGERS") else []
# SSL settings

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = process_false_string(os.getenv("SSL_ONLY", False))
SSLIFY_DISABLE = not process_false_string(os.getenv("SSL_ONLY", False))
site_url = 'http' if SSLIFY_DISABLE else 'https'
SITE_URL = os.getenv('SITE_URL', '')

# Canonical domain -- if this is set, all requests not to this domain will be forwarded to this domain
# this should be a bare domain -- no scheme or route! For instance, www.example.com and not http://www.example.com
CANONICAL_DOMAIN = os.getenv("CANONICAL_DOMAIN", None)

# Application definition

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'curiositymachine',
    'django.contrib.admin',
    'profiles',
    'challenges',
    'cmcomments',
    'videos',
    'images',
    'django_rq',
    'password_reset',
    'pages',
    'django_summernote',
    'django_bleach',
    'training',
    'cmemails',
    'tsl',
    'compressor',
)

MIDDLEWARE_CLASSES = (
    'curiositymachine.middleware.CanonicalDomainMiddleware', # this MUST come before the SSLify middleware or else non-canonical domains that do not have SSL endpoints will not work!
    'sslify.middleware.SSLifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "curiositymachine.middleware.UnderageStudentSandboxMiddleware",
    'curiositymachine.middleware.UnapprovedMentorSandboxMiddleware',
    'curiositymachine.middleware.LastActiveMiddleware',
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
    "curiositymachine.context_processors.google_analytics"
)

AUTH_USER_MODEL = 'auth.User'

ROOT_URLCONF = 'curiositymachine.urls'

WSGI_APPLICATION = 'curiositymachine.wsgi.application'

LOGIN_URL = '/login/'

CSRF_FAILURE_VIEW = 'curiositymachine.views.csrf_failure_handler'

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

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

FILEPICKER_API_KEY = os.getenv("FILEPICKER_API_KEY", "")

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "curiositymachine")
AWS_ERROR_STORAGE_BUCKET_NAME = os.getenv("AWS_ERROR_STORAGE_BUCKET_NAME", "curiositymachine_error_pages")

ZENCODER_API_KEY = os.environ.get("ZENCODER_API_KEY", "")

S3_URL_BASE = "http://s3.amazonaws.com"

MEDIA_URL = S3_URL_BASE + '/' + AWS_STORAGE_BUCKET_NAME + '/'

#job queues
RQ_QUEUES = {
    'default': {
        'URL': os.getenv('REDIS_URL', 'redis://localhost:6379'),
        'DB': 0,}
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get("POSTMARK_SMTP_SERVER", "")
EMAIL_PORT = 25
EMAIL_HOST_USER = os.environ.get("POSTMARK_API_KEY", "")
EMAIL_HOST_PASSWORD = os.environ.get("POSTMARK_API_KEY", "")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")

# Which HTML tags are allowed
BLEACH_ALLOWED_TAGS = ['p', 'b', 'i', 'u', 'em', 'strong', 'a', 'h1', 'h2', 'h3', 'h4', 'br', 'strike', 'li', 'ul', 'div', 'ol', 'span', 'blockquote', 'pre', 'img']

# Which HTML attributes are allowed
BLEACH_ALLOWED_ATTRIBUTES = ['href', 'title', 'class']

BLEACH_LIB_ATTRIBUTES = {
                            '*': ['title', 'style'],
                            'a': ['id', 'href', 'fpfilekey', 'rel', 'class', 'number', 'data-height', 'data-width'],
                            'img': ['src', 'alt', 'width', 'height', 'data-height', 'data-width', 'data-upload', 'class', 'id', 'data-original', 'data-key'],
                            'div' : ['class']
                        }

# Which CSS properties are allowed in 'style' attributes (assuming
# style is an allowed attribute)
BLEACH_ALLOWED_STYLES = ['font-family', 'font-weight', 'text-decoration', 'font-variant']

# Strip unknown tags if True, replace with HTML escaped characters if
# False
BLEACH_STRIP_TAGS = True

# Strip comments, or leave them in.
BLEACH_STRIP_COMMENTS = True

# Use the SummernoteWidget for bleached HTML fields
BLEACH_DEFAULT_WIDGET = 'django_summernote.widgets.SummernoteWidget'

SUMMERNOTE_CONFIG = {
    # Change editor size
    'width': '100%',
    'height': '350',

    # Customize toolbar buttons
    'toolbar': [
        ['style', ['bold', 'italic', 'underline', 'strike']],
        ['style', ['color']],
        ['para', ['ul', 'ol']],
    ],
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console':{
            'level': 'ERROR',
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['console',],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'apptemplates.Loader',
)

EMAIL_INACTIVE_DAYS_MENTOR = os.environ.get("EMAIL_INACTIVE_DAYS_MENTOR", 7)
EMAIL_INACTIVE_DAYS_STUDENT = os.environ.get("EMAIL_INACTIVE_DAYS_STUDENT", 14)
GA_CODE = os.environ.get("GA_CODE", None)
PROGRESS_MONTH_ACTIVE_LIMIT = os.environ.get("PROGRESS_MONTH_ACTIVE_LIMIT", 2)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", None)

# CLOUDINARY_URL is not a config variable; cloudinary reads it directly from the environment.  To override it, run cloudinary.config()

# Import optional local settings.  This must be at the END of this file.
try:
    from .local import *
except ImportError:
    pass
