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