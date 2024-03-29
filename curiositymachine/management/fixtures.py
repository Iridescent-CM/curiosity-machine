import os
from challenges.factories import *
from django.conf import settings
from educators.factories import *
from images.factories import *
from profiles.factories import *
from students.factories import *
from videos.factories import *

from .utils import load_fixture

def basic_users():
    UserFactory(
        email="cmadmin@mailinator.com",
        is_staff=True,
        is_superuser=True,
        username="admin",
        password="123123",
    )

    StudentFactory(
        email="teen@mailinator.com",
        username="teen",
        password="123123",
    )
    EducatorFactory(
        email="educator@mailinator.com",
        username="educator",
        password="123123"
    )

def basic_challenges():
    ChallengeFactory.create_batch(30, draft=False)

def muppet_school():
    load_fixture(os.path.join(settings.BASE_DIR, 'curiositymachine/fixtures/muppet_school.json'))

def aifc():
    # NB: a bunch of .env config has to line up with the fixture data for it to work
    #     e.g. survey and signature ids for family accounts to have full access
    load_fixture(os.path.join(settings.BASE_DIR, 'curiositymachine/fixtures/aifc.json'))