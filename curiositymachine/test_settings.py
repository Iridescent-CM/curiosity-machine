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

# For tests, force no feature flags and override in actual test with e.g.
#       with mock.patch.dict(settings.FEATURE_FLAGS, {'enable_whatever': True}):
#               ...
FEATURE_FLAGS={
    'enable_challenge_preview_restriction': True
}