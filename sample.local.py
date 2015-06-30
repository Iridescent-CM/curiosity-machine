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

## Email addresses
# Try not to spam strangers! Addresses at example.com or example.org should
# go nowhere, or you can use something like mailinator (http://mailinator.com/)
DEFAULT_FROM_EMAIL  = 'default_from_email@example.org'
MENTOR_RELATIONSHIP_MANAGERS = ['mentor_relationship_manager@example.org']

## Addon keys

# Access to S3 development bucket
AWS_ACCESS_KEY_ID = 'AKIAIFGEY6CNUQ7YYCHQ'
AWS_SECRET_ACCESS_KEY = 't26j6SUmpPaacf76adb/QSwYucZQ1NHd0OTQGugn'
AWS_STORAGE_BUCKET_NAME = 'devcuriositymachine'

# The filepicker key and secret are also used in staging. You can set up your own
# account and replace these if desired.
FILEPICKER_API_KEY = 'AGMpw9ALPRTObV0qAHZKJz'
FILEPICKER_API_SECRET = 'A3KXG3UOK5HPTLKML6AIBJ54XA'

# Zencoder integration mode api key, same as staging. 
ZENCODER_API_KEY = '44f49037d18313505855f0920a70bd5a'
