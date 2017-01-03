from .settings import *
import os

if not REDIS_TEST_URL:
    raise Exception("Set REDIS_TEST_URL in the environment or your local.py")

REDIS_URL = REDIS_TEST_URL
RQ_QUEUES = {
    'default': {
        'URL': REDIS_URL,
        'DB': None # take from REDIS_URL instead
    }
}

# We generally don't want to rely on S3 for tests (and can override settings when we do)
DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"

# If testing generates files, stick them in a temporary location
from tempfile import gettempdir
MEDIA_ROOT = gettempdir()

# For tests, force no feature flags and override in actual test with e.g.
#       with mock.patch.dict(settings.FEATURE_FLAGS, {'enable_whatever': True}):
#               ...
FEATURE_FLAGS={
}