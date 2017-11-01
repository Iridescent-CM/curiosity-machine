# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


## dotenv
# Get a .env file from another developer for reasonable development defaults
from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv(find_dotenv())


## Debug, tests, dev tools
DEBUG = os.environ.get('DEBUG', False) # debug saves a LOT of info and should never be left on in production

DEBUG_TOOLBAR = os.environ.get('DEBUG_TOOLBAR', False)
DEBUG_HTML = os.environ.get('DEBUG_HTML', False)
USE_DJANGO_EXTENSIONS = os.environ.get('USE_DJANGO_EXTENSIONS', False)

TEST_RUNNER = "django_pytest.test_runner.TestRunner"


## Database
import dj_database_url
DATABASES = {
        "default": dj_database_url.config(default='postgres://localhost:5432/cm_local'),
}

# Redis & rq
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DB': None # take from REDIS_URL instead
    }
}


## SSL settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = os.getenv("SSL_ONLY", False)
SSLIFY_DISABLE = not os.getenv("SSL_ONLY", False)
SITE_URL = os.getenv('SITE_URL', '')


## Application definition
ADMINS = tuple([("Curiosity Machine Admin", email) for email in os.getenv("ADMINS", '').split(',')])

# Canonical domain -- if this is set, all requests not to this domain will be forwarded to this domain
# this should be a bare domain -- no scheme or route! For instance, www.example.com and not http://www.example.com
CANONICAL_DOMAIN = os.getenv("CANONICAL_DOMAIN", None)

COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED', False) # no compression by default for now

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", '0!)smlfbaj=4w7a=@#%5_5h*+n38m2c165xpbn9^#z_a%kgwrs')

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", '').split(',') if os.getenv("ALLOWED_HOSTS") else []

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_summernote',
    'curiositymachine',
    'django.contrib.admin',
    'django.contrib.sites',
    'django.contrib.flatpages',
    'profiles',
    'challenges',
    'cmcomments',
    'videos',
    'images',
    'django_rq',
    'password_reset',
    'cmemails',
    'compressor',
    'units',
    's3direct',
    'memberships',
    'quizzes',
    'widget_tweaks',
    'rest_framework',
    'notifications',
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
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.request",
                "curiositymachine.context_processors.login_and_join_forms",
                "curiositymachine.context_processors.google_analytics",
                "curiositymachine.context_processors.feature_flags",
                "curiositymachine.context_processors.template_globals",
                "curiositymachine.context_processors.staff_alerts",
            ],
            'loaders': [
                'apptemplates.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger'
}

AUTH_USER_MODEL = 'auth.User'

ROOT_URLCONF = 'curiositymachine.urls'

WSGI_APPLICATION = 'curiositymachine.wsgi.application'

LOGIN_URL = '/login/'

CSRF_FAILURE_VIEW = 'curiositymachine.views.csrf_failure_handler'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = 'staticfiles'
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

# File storage
DEFAULT_FILE_STORAGE = "django_s3_storage.storage.S3Storage"

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "")

EMAIL_HOST = os.environ.get("MANDRILL_SMTP_SERVER", "")
EMAIL_PORT = os.environ.get("MANDRILL_SMTP_PORT", "")
EMAIL_HOST_USER = os.environ.get("MANDRILL_SMTP_USERNAME", "")
EMAIL_HOST_PASSWORD = os.environ.get("MANDRILL_API_KEY", "")

EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", True)
EMAIL_USE_SSL = False

# Summernote
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

# Logging
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
        'django.server': {
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

# Additional app config
GA_CODE = os.environ.get("GA_CODE", None)

SITE_MESSAGE = os.environ.get("SITE_MESSAGE", None)
SITE_MESSAGE_LEVEL = os.environ.get("SITE_MESSAGE_LEVEL", None)

MENTOR_RELATIONSHIP_MANAGERS = os.getenv("MENTOR_RELATIONSHIP_MANAGERS", '').split(',') if os.getenv("MENTOR_RELATIONSHIP_MANAGERS") else []
NOTIFICATION_RECIPIENTS = os.getenv("NOTIFICATION_RECIPIENTS").split(',') if os.getenv("NOTIFICATION_RECIPIENTS") else []
MEMBER_IMPORT_EXPIRATION_DAYS = os.environ.get("MEMBER_IMPORT_EXPIRATION_DAYS", 7)
MEMBERSHIP_EXPIRING_NOTICE_DAYS = os.environ.get("MEMBER_EXPIRING_NOTICE_DAYS", 30)
MEMBERSHIP_EXPIRED_NOTICE_DAYS = os.environ.get("MEMBER_EXPIRED_NOTICE_DAYS", 30)
EMAIL_INACTIVE_DAYS_MENTOR = os.environ.get("EMAIL_INACTIVE_DAYS_MENTOR", 7)
EMAIL_INACTIVE_DAYS_STUDENT = os.environ.get("EMAIL_INACTIVE_DAYS_STUDENT", 14)
PROGRESS_MONTH_ACTIVE_LIMIT = os.environ.get("PROGRESS_MONTH_ACTIVE_LIMIT", 2)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", None)
REQUEST_A_MENTOR_LINK = os.environ.get("REQUEST_A_MENTOR_LINK", None)
DOCEBO_MENTOR_URL = os.environ.get("DOCEBO_MENTOR_URL","http://www.iridescentuniversity.org/lms/")

# pagination
CHALLENGES_PER_PAGE = os.environ.get("CHALLENGES_PER_PAGE", 9)
MD_PAGE_SIZE = os.environ.get("MD_PAGE_SIZE", 16)
DEFAULT_PER_PAGE = os.environ.get("DEFAULT_PER_PAGE", 12)

# URL blacklist/whitelist
# an impossible pattern below prevents blacklisting until actual patterns are provided through the env
BLACKLIST_URLS = map(str.strip, os.environ.get('BLACKLIST_URLS', 'a^').split(','))
WHITELIST_URLS = map(str.strip, os.environ.get('WHITELIST_URLS', '^admin/?').split(','))

# Feature flags
# Any environment variable beginning with ENABLE_ will end up in template contexts
# as flags.enable_ and can be used in the feature_flag() decorator.
FEATURE_FLAGS = {k.lower(): v for k, v in os.environ.items() if k.startswith('ENABLE_')}


## External service configuration

# Filepicker
FILEPICKER_API_KEY = os.getenv("FILEPICKER_API_KEY", "")
FILEPICKER_MAX_VIDEO_LENGTH_SECONDS = os.getenv("FILEPICKER_MAX_VIDEO_LENGTH", 60*2)

# AWS, S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "curiositymachine")
AWS_S3_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"

S3DIRECT_REGION = os.getenv("S3DIRECT_REGION", "us-east-1")
S3DIRECT_DESTINATIONS = {
    'unit-resources': (
        'units/resources',
        lambda u: u.is_staff,
    ),
    'admin-videos': (
        'videos/sources',
        lambda u: u.is_staff,
    ),
    'admin-images': (
        'images/sources',
        lambda u: u.is_staff,
    ),
}
S3_URL_BASE = "https://s3.amazonaws.com"

AWS_REGION = S3DIRECT_REGION

MEDIA_URL = S3_URL_BASE + '/' + AWS_STORAGE_BUCKET_NAME + '/'

# Mandrill & Mailchimp
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

# Zencoder
ZENCODER_API_KEY = os.environ.get("ZENCODER_API_KEY", "")
REPORT_ZENCODER_USAGE = os.environ.get("REPORT_ZENCODER_USAGE", False)

# CLOUDINARY_URL is not a config variable; cloudinary reads it directly from the environment.  To override it, run cloudinary.config()

# Rollbar
ROLLBAR_CLIENT_SIDE_ACCESS_TOKEN = os.environ.get("ROLLBAR_CLIENT_SIDE_ACCESS_TOKEN", "")
ROLLBAR_SERVER_SIDE_ACCESS_TOKEN = os.environ.get("ROLLBAR_SERVER_SIDE_ACCESS_TOKEN", "")
ROLLBAR_ENV = os.environ.get("ROLLBAR_ENV", "default")


## Conditional apps or middleware 

if ROLLBAR_SERVER_SIDE_ACCESS_TOKEN:
    from django.http import Http404
    from curiositymachine.exceptions import LoginRequired
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

if DEBUG and DEBUG_TOOLBAR:
    INSTALLED_APPS += ('debug_toolbar',)

if USE_DJANGO_EXTENSIONS:
    INSTALLED_APPS += ('django_extensions',)

if DEBUG and DEBUG_HTML:
    HTMLVALIDATOR_ENABLED = True
    HTMLVALIDATOR_FAILFAST = os.environ.get("HTMLVALIDATOR_FAILFAST", False)
    HTMLVALIDATOR_OUTPUT = 'stdout'  # default is 'file'
    HTMLVALIDATOR_VNU_URL = 'http://localhost:8888/' # run with `java -cp vnu.jar nu.validator.servlet.Main 8888`
    MIDDLEWARE_CLASSES += ("htmlvalidator.middleware.HTMLValidator",)
