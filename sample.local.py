import dj_database_url
import os

#
# This file provides a fairly complete sample configuration file for
# local development, with sensible defaults provided where appropriate.
#
# To use it, copy it to curiositymachine/local.py and edit as needed for
# your setup.
#

## Debug
DEBUG = True
TEMPLATE_DEBUG = True

## Site config
SITE_URL = 'http://localhost:8000'

## Database
# Change <user> and <dbname> as appropriate, or you can
# change DATABASE_URL entirely
DATABASE_URL = 'postgres://<user>@localhost:5432/<dbname>'
DATABASES = {
    "default": dj_database_url.config(default=DATABASE_URL),
}

## Django RQ and Redis
# For development mode, usually redis is on 6379 on localhost
# so there may be nothing to change here. The Django RQ configuration
# uses REDIS_URL as well. Uncomment the lines below to change if desired.
# REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
# RQ_QUEUES = {
#     'default': {
#         'URL': REDIS_URL,
#         'DB': None # take from REDIS_URL instead
#     }
# }
#
# Tests will flush the Redis database, so you can use the config below
# to point it at a different instance or db.
REDIS_TEST_URL = os.getenv('REDIS_TEST_URL', 'redis://localhost:6379/1')

## Email
# NOTE: we are migrating to use the Mandrill API for email, and emailing sending is
# temporarily split between Mandrill and Django's built-in email functionality
#
# SMTP
# You can send email through a properly configured gmail account, or use
# a tool like FakeSMTP (http://nilhcem.github.io/FakeSMTP/) to keep it all local.
# Comment/uncomment the following sections as appropriate for your approach.
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Example FakeSMTP setup
EMAIL_HOST      = 'localhost'
EMAIL_PORT      = 8001
EMAIL_USE_TLS   = False

# Example Gmail setup
# Change <pass> and <email>, and make sure your account is set up to
# allow access: https://support.google.com/accounts/answer/6010255
# EMAIL_HOST      = 'smtp.gmail.com'
# EMAIL_HOST_PASSWORD = '<pass>'
# EMAIL_HOST_USER = '<email>@gmail.com'
# EMAIL_PORT      = 587
# EMAIL_USE_TLS   = True

# Mandrill
# For local development, using a test key will segregate test API calls from real ones, and
# will incur no per-email cost. Emails will not be sent, but will be viewable through the
# Mandrill dashboard if put into test mode.
MANDRILL_API_KEY = ''
# A prefix, if provided, will be prepended to template names when making API calls.
MANDRILL_TEMPLATE_PREFIX = ''
MANDRILL_MESSAGE_DEFAULTS = {
    "auto_text": True,
    "inline_css": True,
    "merge_language": "handlebars",
}

## Email addresses
# Try not to spam strangers! Addresses at example.com or example.org should
# go nowhere, or you can use something like mailinator (http://mailinator.com/)
DEFAULT_FROM_EMAIL  = 'default_from_email@example.org'
MENTOR_RELATIONSHIP_MANAGERS = ['mentor_relationship_manager@example.org']

## Mailing lists
# New users are auto-subscribed to Mailchimp mailing lists if proper
# configuration is provided. Omitting the Mailchimp API key will not
# cause an error, but simply skip the mailing list sign-up.
MAILCHIMP_API_KEY = ''
# The data center is part of the url, and corresponds to the data center for
# the Mailchimp account. It's the last part of the API key, e.g. if the key
# is abc123-us4 the data center is us4.
# http://developer.mailchimp.com/documentation/mailchimp/guides/get-started-with-mailchimp-api-3/#resources
MAILCHIMP_DATA_CENTER = ''
# To sign up users to lists, populate this dictionary with key/value pairs where the key
# is the user type and the value is the list id. Alternatively, delete the following line and
# provide environmental configuration of the pattern MAILCHIMP_LIST_ID_<type>=<id>.
MAILCHIMP_LIST_IDS = {}

## Addon keys

# Access to S3 development bucket
AWS_ACCESS_KEY_ID = 'AKIAIFGEY6CNUQ7YYCHQ'
AWS_SECRET_ACCESS_KEY = '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'
AWS_S3_BUCKET_NAME = AWS_STORAGE_BUCKET_NAME = 'devcuriositymachine'

# The filepicker key and secret are also used in staging. You can set up your own
# account and replace these if desired.
FILEPICKER_API_KEY = 'AGMpw9ALPRTObV0qAHZKJz'
FILEPICKER_API_SECRET = 'A3KXG3UOK5HPTLKML6AIBJ54XA'

# Zencoder integration-only api key
ZENCODER_API_KEY = '81382e6f5779989ca5d9f97ca9e271d6'

# put Cloudinary URL in the environment, so image sizes aren't all wrong
os.environ['CLOUDINARY_URL'] = 'cloudinary://288919217452943:y0vtMjjVXEUUDr5vesV1_zc4z3c@hhm2kh41m'
