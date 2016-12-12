"""
Django settings for curiositymachine project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import dj_database_url
from django.http import Http404
from curiositymachine.exceptions import LoginRequired

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

TEST_RUNNER = "django_pytest.test_runner.TestRunner"

DEBUG_TOOLBAR = os.environ.get('DEBUG_TOOLBAR', False)
DEBUG_HTML = os.environ.get('DEBUG_HTML', False)

COMPRESS_ENABLED = process_false_string(os.environ.get('COMPRESS_ENABLED', False)) # no compression by default for now

ADMINS = tuple([("Curiosity Machine Admin", email) for email in os.getenv("ADMINS", '').split(',')])

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", '0!)smlfbaj=4w7a=@#%5_5h*+n38m2c165xpbn9^#z_a%kgwrs')

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", '').split(',') if os.getenv("ALLOWED_HOSTS") else []
MENTOR_RELATIONSHIP_MANAGERS = os.getenv("MENTOR_RELATIONSHIP_MANAGERS", '').split(',') if os.getenv("MENTOR_RELATIONSHIP_MANAGERS") else []
NOTIFICATION_RECIPIENTS = os.getenv("NOTIFICATION_RECIPIENTS").split(',') if os.getenv("NOTIFICATION_RECIPIENTS") else []

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
    'django.contrib.sites',
    'django.contrib.flatpages',
    'staticflatpages',
    'profiles',
    'challenges',
    'cmcomments',
    'videos',
    'images',
    'django_rq',
    'password_reset',
    'django_summernote',
    'django_bleach',
    'cmemails',
    'compressor',
    'units',
    's3direct',
    'groups',
    'memberships',
    'widget_tweaks',
    'rest_framework',
)

SITE_ID = 1

MIDDLEWARE_CLASSES = (
    'curiositymachine.middleware.CanonicalDomainMiddleware', # this MUST come before the SSLify middleware or else non-canonical domains that do not have SSL endpoints will not work!
    'sslify.middleware.SSLifyMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'curiositymachine.middleware.LoginRequiredMiddleware',
    "curiositymachine.middleware.UnderageStudentSandboxMiddleware",
    'curiositymachine.middleware.UnapprovedMentorSandboxMiddleware',
    'curiositymachine.middleware.LastActiveMiddleware',
    'curiositymachine.middleware.FirstLoginMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    'staticflatpages.middleware.StaticFlatpageFallbackMiddleware',
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
    "curiositymachine.context_processors.google_analytics",
    "curiositymachine.context_processors.feature_flags",
    "curiositymachine.context_processors.template_globals",
    "curiositymachine.context_processors.staff_alerts",
)

# Any environment variable beginning with ENABLE_ will end up in template contexts
# as flags.enable_ and can be used in the feature_flag() decorator.
FEATURE_FLAGS = {k.lower(): process_false_string(v) for k, v in os.environ.items() if k.startswith('ENABLE_')}

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

DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger'
}

FILEPICKER_API_KEY = os.getenv("FILEPICKER_API_KEY", "")

# upload_to_s3 task settings
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "curiositymachine")

# s3direct
S3DIRECT_REGION = os.getenv("S3DIRECT_REGION", "us-east-1")
S3DIRECT_DESTINATIONS = {
    'unit-resources': (
        'units/resources',
        lambda u: u.is_staff,
    )
}

# django-s3-storage
AWS_REGION = S3DIRECT_REGION
AWS_S3_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"

ZENCODER_API_KEY = os.environ.get("ZENCODER_API_KEY", "")
REPORT_ZENCODER_USAGE = os.environ.get("REPORT_ZENCODER_USAGE", False)

S3_URL_BASE = "http://s3.amazonaws.com"

MEDIA_URL = S3_URL_BASE + '/' + AWS_STORAGE_BUCKET_NAME + '/'

REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DB': None # take from REDIS_URL instead
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.environ.get("POSTMARK_SMTP_SERVER", "")
EMAIL_PORT = 25
EMAIL_HOST_USER = os.environ.get("POSTMARK_API_KEY", "")
EMAIL_HOST_PASSWORD = os.environ.get("POSTMARK_API_KEY", "")
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")

MANDRILL_API_KEY = os.environ.get("MANDRILL_API_KEY", "")
MANDRILL_TEMPLATE_PREFIX = os.environ.get("MANDRILL_TEMPLATE_PREFIX", "")
MANDRILL_MESSAGE_DEFAULTS = {
    "auto_text": True,
    "inline_css": True,
    "merge_language": "handlebars",
}

MAILCHIMP_API_KEY = os.environ.get("MAILCHIMP_API_KEY", "")
MAILCHIMP_DATA_CENTER = os.environ.get("MAILCHIMP_DATA_CENTER", "")
MAILCHIMP_LIST_IDS = {
    k.replace("MAILCHIMP_LIST_ID_", "").replace("_", " ").lower(): v
    for k, v
    in os.environ.items()
    if k.startswith('MAILCHIMP_LIST_ID_')
}

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

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': 'severity=%(levelname)s logger=%(name)s message="%(message)s"'
        },
    },
    'handlers': {
        'console':{
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console',],
            'level': 'DEBUG',
        },
        'django': {
            'handlers': ['console',],
            'level': 'DEBUG',
        },
        'django.request': {
            'handlers': ['console',],
            'level': 'DEBUG',
        },
        'django.security': {
            'handlers': ['console',],
            'level': 'DEBUG',
        },
        'rq.worker': {
            'handlers': ['console',],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    'apptemplates.Loader',
)

MEMBER_IMPORT_EXPIRATION_DAYS = os.environ.get("MEMBER_IMPORT_EXPIRATION_DAYS", 7)
EMAIL_INACTIVE_DAYS_MENTOR = os.environ.get("EMAIL_INACTIVE_DAYS_MENTOR", 7)
EMAIL_INACTIVE_DAYS_STUDENT = os.environ.get("EMAIL_INACTIVE_DAYS_STUDENT", 14)
GA_CODE = os.environ.get("GA_CODE", None)
PROGRESS_MONTH_ACTIVE_LIMIT = os.environ.get("PROGRESS_MONTH_ACTIVE_LIMIT", 2)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", None)
REQUEST_A_MENTOR_LINK = os.environ.get("REQUEST_A_MENTOR_LINK", None)
SITE_MESSAGE = os.environ.get("SITE_MESSAGE", None)
SITE_MESSAGE_LEVEL = os.environ.get("SITE_MESSAGE_LEVEL", None)
DOCEBO_MENTOR_URL = os.environ.get("DOCEBO_MENTOR_URL","http://www.iridescentuniversity.org/lms/")

# pagination
CHALLENGES_PER_PAGE = os.environ.get("CHALLENGES_PER_PAGE", 9)
MD_PAGE_SIZE = os.environ.get("MD_PAGE_SIZE", 16)
DEFAULT_PER_PAGE = os.environ.get("DEFAULT_PER_PAGE", 12)

# an impossible pattern below prevents blacklisting until actual patterns are provided through the env
BLACKLIST_URLS = map(str.strip, os.environ.get('BLACKLIST_URLS', 'a^').split(','))
WHITELIST_URLS = map(str.strip, os.environ.get('WHITELIST_URLS', '^admin/?').split(','))

# CLOUDINARY_URL is not a config variable; cloudinary reads it directly from the environment.  To override it, run cloudinary.config()

# Rollbar
ROLLBAR_CLIENT_SIDE_ACCESS_TOKEN = os.environ.get("ROLLBAR_CLIENT_SIDE_ACCESS_TOKEN", "")
ROLLBAR_SERVER_SIDE_ACCESS_TOKEN = os.environ.get("ROLLBAR_SERVER_SIDE_ACCESS_TOKEN", "")
ROLLBAR_ENV = os.environ.get("ROLLBAR_ENV", "default")


# Import optional local settings.  This must come after config you want to be able to override, but before it's usage.
try:
    from .local import *
except ImportError:
    pass

# Do this after importing local.py so it can swap out the env parameters if desired
if ROLLBAR_SERVER_SIDE_ACCESS_TOKEN:
    ROLLBAR = {
        'access_token': ROLLBAR_SERVER_SIDE_ACCESS_TOKEN,
        'environment': ROLLBAR_ENV,
        'branch': 'master',
        'root': os.getcwd(),
        'exception_level_filters': [
            (Http404, 'ignored'),
            (LoginRequired, 'ignored'),
        ]
    }
    MIDDLEWARE_CLASSES += ('rollbar.contrib.django.middleware.RollbarNotifierMiddleware',)

# Conditionally install the debug toolbar
if DEBUG and DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)

if DEBUG and DEBUG_HTML:
    HTMLVALIDATOR_ENABLED = True
    HTMLVALIDATOR_FAILFAST = os.environ.get("HTMLVALIDATOR_FAILFAST", False)
    HTMLVALIDATOR_OUTPUT = 'stdout'  # default is 'file'
    HTMLVALIDATOR_VNU_URL = 'http://localhost:8888/' # run with `java -cp vnu.jar nu.validator.servlet.Main 8888`
    MIDDLEWARE_CLASSES += ("htmlvalidator.middleware.HTMLValidator",)
