import os

from dotenv import load_dotenv, find_dotenv
if find_dotenv():
    load_dotenv(find_dotenv())

# Swap in REDIS_TEST_URL for REDIS_URL
if not os.getenv('REDIS_TEST_URL'):
    raise Exception("Set REDIS_TEST_URL in the environment or your .env")
os.environ['REDIS_URL'] = os.getenv('REDIS_TEST_URL', "")

from .settings import *

# We generally don't want to rely on S3 for tests (and can override settings when we do)
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# If testing generates files, stick them in a temporary location
from tempfile import gettempdir
MEDIA_ROOT = gettempdir()

# Set up the rest_framework test client
REST_FRAMEWORK = {
    'TEST_REQUEST_DEFAULT_FORMAT': 'json'
}

# Don't let whitenoise slow things down too much
WHITENOISE_AUTOREFRESH=True

# For tests, force no feature flags and override in actual test with e.g.
#       with mock.patch.dict(settings.FEATURE_FLAGS, {'enable_whatever': True}):
#               ...
FEATURE_FLAGS={
    'ENABLE_IMPACT_SURVEY': 1
}