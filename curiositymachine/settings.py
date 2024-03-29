# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from django.utils.dateparse import parse_datetime
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
SECURE_SSL_REDIRECT = os.getenv('SSL_ONLY', False)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = os.getenv('SSL_ONLY', False)

SITE_URL = os.getenv('SITE_URL', '')
PREPEND_WWW = os.getenv('PREPEND_WWW', False)


## Application definition
ADMINS = tuple([("Curiosity Machine Admin", email) for email in os.getenv("ADMINS", '').split(',')])
INTERNAL_IPS = os.getenv('INTERNAL_IPS', '').split(',') if os.getenv('INTERNAL_IPS') else []

COMPRESS_ENABLED = os.environ.get('COMPRESS_ENABLED', False) # no compression by default for now

WEBPACK_LOADER = {
    'DEFAULT': {
        'BUNDLE_DIR_NAME': 'js/webpack_bundles/' if DEBUG else 'js/dist/',
        'STATS_FILE': os.path.join(BASE_DIR, 'curiositymachine/assets/webpack-stats.json' if DEBUG else 'curiositymachine/assets/webpack-stats-prod.json'),
    }
}

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
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'profiles',
    'locations.apps.LocationsConfig',
    'students',
    'educators',
    'families.apps.FamiliesConfig',
    'challenges',
    'lessons',
    'cmcomments',
    'videos',
    'images',
    'season_markers.apps.SeasonMarkersConfig',
    'documents',
    'django_rq',
    'hellosign.apps.HellosignConfig',
    'surveys.apps.SurveysConfig',
    'cmemails',
    'compressor',
    'units',
    's3direct',
    'memberships',
    'quizzes',
    'widget_tweaks',
    'rest_framework',
    'notifications',
    'debug_toolbar',
    'feedback',
    'django_ace',
    'ordered_model',
    'webpack_loader',
)

SITE_ID = 1

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'curiositymachine.middleware.UserProxyMiddleware',
    'curiositymachine.middleware.LoginRequiredMiddleware',
    "curiositymachine.middleware.UnapprovedStudentSandboxMiddleware",
    'curiositymachine.middleware.LastActiveMiddleware',
    'curiositymachine.middleware.FirstLoginMiddleware',
    'families.middleware.SignUpPrerequisitesMiddleware',
    'season_markers.middleware.SeasonParticipationMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
]

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
                "curiositymachine.context_processors.login_form",
                "curiositymachine.context_processors.google_analytics",
                "curiositymachine.context_processors.feature_flags",
                "curiositymachine.context_processors.template_globals",
                "curiositymachine.context_processors.staff_alerts",
                "curiositymachine.context_processors.emails",
            ],
            'loaders': [
                'apptemplates.Loader',
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]
        },
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

from django.contrib.messages import constants as message_constants
MESSAGE_TAGS = {
    message_constants.INFO: 'alert-info',
    message_constants.SUCCESS: 'alert-success',
    message_constants.WARNING: 'alert-warning',
    message_constants.ERROR: 'alert-danger'
}

AUTH_USER_MODEL = 'auth.User'
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 6,
        }
    },
]

ACCOUNT_ADAPTER = 'curiositymachine.allauth_adapter.AllAuthAdapter'
ACCOUNT_USERNAME_VALIDATORS = 'curiositymachine.validators.username_validators'
ACCOUNT_SIGNUP_FORM_CLASS = 'curiositymachine.forms.SignupExtraForm'
ACCOUNT_SIGNUP_HONEYPOT_FIELD = 'phonenumber'
ACCOUNT_AUTHENTICATED_LOGIN_REDIRECTS = False
ACCOUNT_UNIQUE_EMAIL = False
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_SESSION_REMEMBER = True

ROOT_URLCONF = 'curiositymachine.urls'

WSGI_APPLICATION = 'curiositymachine.wsgi.application'

LOGIN_URL = 'account_login'
LOGIN_REDIRECT_URL = 'root'

CSRF_FAILURE_VIEW = 'curiositymachine.views.csrf_failure_handler'

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = "America/Los_Angeles"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'
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

NOTIFICATIONS_USE_JSONFIELD = True

# Additional app config
GA_CODE = os.environ.get("GA_CODE", None)
GTM_CONTAINER_ID = os.environ.get("GTM_CONTAINER_ID", None)

SITE_MESSAGE = os.environ.get("SITE_MESSAGE", None)
SITE_MESSAGE_LEVEL = os.environ.get("SITE_MESSAGE_LEVEL", None)

AICHALLENGE_STAGES = {
    1: {
        "challenges": [int(i) for i in os.getenv("AICHALLENGE_STAGE_1_CHALLENGES", "").split(',') if i],
        "units": [int(i) for i in os.getenv("AICHALLENGE_STAGE_1_UNITS", "").split(',') if i],
    },
    2: {
        "challenges": [int(i) for i in os.getenv("AICHALLENGE_STAGE_2_CHALLENGES", "").split(',') if i],
        "units": [int(i) for i in os.getenv("AICHALLENGE_STAGE_2_UNITS", "").split(',') if i],
    },
    3: {
        # just pull all lessons for now
    },
}
AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID=os.getenv("AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID", "")
AICHALLENGE_SEASON_OPEN=os.getenv('AICHALLENGE_SEASON_OPEN', False)

SEASON_MARKER_START_DATETIME=parse_datetime(os.getenv('SEASON_MARKER_START_DATETIME')) if os.getenv('SEASON_MARKER_START_DATETIME') else None
SEASON_MARKER_END_DATETIME=parse_datetime(os.getenv('SEASON_MARKER_END_DATETIME')) if os.getenv('SEASON_MARKER_END_DATETIME') else None
SEASON_MARKER_NAME=os.getenv('SEASON_MARKER_NAME')

NOTIFICATION_RECIPIENTS = os.getenv("NOTIFICATION_RECIPIENTS").split(',') if os.getenv("NOTIFICATION_RECIPIENTS") else []
MEMBER_IMPORT_EXPIRATION_DAYS = os.environ.get("MEMBER_IMPORT_EXPIRATION_DAYS", 7)
MEMBERSHIP_EXPIRING_NOTICE_DAYS = os.environ.get("MEMBER_EXPIRING_NOTICE_DAYS", 30)
MEMBERSHIP_EXPIRED_NOTICE_DAYS = os.environ.get("MEMBER_EXPIRED_NOTICE_DAYS", 30)
EMAIL_INACTIVE_DAYS_STUDENT = os.environ.get("EMAIL_INACTIVE_DAYS_STUDENT", 14)
EMAIL_INACTIVE_DAYS_FAMILY = os.environ.get("EMAIL_INACTIVE_DAYS_FAMILY", 14)
PROGRESS_MONTH_ACTIVE_LIMIT = os.environ.get("PROGRESS_MONTH_ACTIVE_LIMIT", 2)
CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", None)

# pagination
CHALLENGES_PER_PAGE = os.environ.get("CHALLENGES_PER_PAGE", 9)
MD_PAGE_SIZE = os.environ.get("MD_PAGE_SIZE", 16)
DEFAULT_PER_PAGE = os.environ.get("DEFAULT_PER_PAGE", 12)

# URL blacklist/whitelist
# an impossible pattern below prevents blacklisting until actual patterns are provided through the env
BLACKLIST_URLS = map(str.strip, os.environ.get('BLACKLIST_URLS', 'a^').split(','))
WHITELIST_URLS = map(str.strip, os.environ.get('WHITELIST_URLS', '^admin/?,accounts/?,memberships/?').split(','))

# Feature flags
# Any environment variable beginning with ENABLE_ will end up in template contexts
# as flags.enable_ and can be used in the feature_flag() decorator.
FEATURE_FLAGS = {k.lower(): v for k, v in os.environ.items() if k.startswith('ENABLE_')}

# Parent account deprecation
DEPRECATE_PARENT_ACCOUNTS = os.environ.get("DEPRECATE_PARENT_ACCOUNTS", None)


## External service configuration

# Filepicker
FILEPICKER_API_KEY = os.getenv("FILEPICKER_API_KEY", "")
FILEPICKER_MAX_VIDEO_LENGTH_SECONDS = os.getenv("FILEPICKER_MAX_VIDEO_LENGTH_SECONDS", 60*2)

# AWS, S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME", "curiositymachine")
AWS_S3_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME
AWS_S3_CALLING_FORMAT = "boto.s3.connection.OrdinaryCallingFormat"
AWS_S3_CONTENT_DISPOSITION = "inline"

S3DIRECT_REGION = os.getenv("S3DIRECT_REGION", "us-east-1")
S3DIRECT_DESTINATIONS = {
    'unit-resources': {
        'key': 'units/resources',
        'auth': lambda u: u.is_staff,
        'content_disposition': 'inline',
    },
    'admin-videos': {
        'key': 'videos/sources',
        'auth': lambda u: u.is_staff,
        'content_disposition': 'inline',
    },
    'admin-images': {
        'key': 'images/sources',
        'auth': lambda u: u.is_staff,
        'content_disposition': 'inline',
    },
    'admin-documents': {
        'key': 'documents/sources',
        'auth': lambda u: u.is_staff,
    },
}
S3_URL_BASE = "https://s3.amazonaws.com"

AWS_REGION = S3DIRECT_REGION

MEDIA_URL = S3_URL_BASE + '/' + AWS_STORAGE_BUCKET_NAME + '/'

# Hellosign e-signature
HELLOSIGN_API_KEY = os.environ.get("HELLOSIGN_API_KEY", "")
UNDERAGE_CONSENT_TEMPLATE_ID = os.environ.get("UNDERAGE_CONSENT_TEMPLATE_ID", "")
UNDERAGE_CONSENT_TEMPLATE_USERNAME_ID = os.environ.get("UNDERAGE_CONSENT_TEMPLATE_USERNAME_ID", "")
UNDERAGE_CONSENT_TEMPLATE_BIRTHDAY_ID = os.environ.get("UNDERAGE_CONSENT_TEMPLATE_BIRTHDAY_ID", "")
UNDERAGE_CONSENT_TEMPLATE_EMAIL_ID = os.environ.get("UNDERAGE_CONSENT_TEMPLATE_EMAIL_ID", "")
HELLOSIGN_PRODUCTION_MODE = os.environ.get("HELLOSIGN_PRODUCTION_MODE", False)
HELLOSIGN_ENVIRONMENT_NAME = os.environ.get("HELLOSIGN_ENVIRONMENT_NAME", None)

# Hellosign templates
HELLOSIGN_TEMPLATE_FAMILY_CONSENT_ID = "abc123"
HELLOSIGN_TEMPLATE_STUDENT_CONSENT_ID = "def456"
for k, v in os.environ.items():
    if k.startswith("HELLOSIGN_TEMPLATE_"):
        setattr(sys.modules[__name__], k, v)

# Surveymonkey
SURVEYMONKEY_API_KEY = os.environ.get("SURVEYMONKEY_API_KEY", "")
SURVEYMONKEY_API_SECRET = os.environ.get("SURVEYMONKEY_API_SECRET", "")
SURVEYMONKEY_ACCESS_TOKEN = os.environ.get("SURVEYMONKEY_ACCESS_TOKEN", "")
SURVEYMONKEY_TOKEN_VAR = os.environ.get("SURVEYMONKEY_TOKEN_VAR", "cmtoken")
SURVEYMONKEY_API_BASE_URL = os.environ.get("SURVEYMONKEY_API_BASE_URL", "https://api.surveymonkey.net/v3/")

# Survey and survey webhook config
for k, v in os.environ.items():
    if k.startswith("SURVEY_"):
        setattr(sys.modules[__name__], k, v)
ALLOW_SURVEY_RESPONSE_HOOK_BYPASS = os.environ.get("ALLOW_SURVEY_RESPONSE_HOOK_BYPASS", False)

# Award Force integration
AWARDFORCE_API_KEY = os.environ.get("AWARDFORCE_API_KEY", "")
AWARDFORCE_ACCOUNT_ID = os.environ.get("AWARDFORCE_ACCOUNT_ID", "")

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
ROLLBAR_VERBOSE = os.environ.get("ROLLBAR_VERBOSE", None)


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
    MIDDLEWARE.append('rollbar.contrib.django.middleware.RollbarNotifierMiddleware')

DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": 'curiositymachine.debug.show_toolbar'
}

if USE_DJANGO_EXTENSIONS:
    INSTALLED_APPS += ('django_extensions',)

if DEBUG and DEBUG_HTML:
    HTMLVALIDATOR_ENABLED = True
    HTMLVALIDATOR_FAILFAST = os.environ.get("HTMLVALIDATOR_FAILFAST", False)
    HTMLVALIDATOR_OUTPUT = 'stdout'  # default is 'file'
    HTMLVALIDATOR_VNU_URL = 'http://localhost:8888/' # run with `java -cp vnu.jar nu.validator.servlet.Main 8888`
    MIDDLEWARE.append("htmlvalidator.middleware.HTMLValidator")
