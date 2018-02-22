import os
from challenges.factories import *
from django.conf import settings
from educators.factories import *
from images.factories import *
from mentors.factories import *
from parents.factories import *
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
        email="child@mailinator.com",
        username="child",
        password="123123",
        studentprofile__underage=True
    )
    StudentFactory(
        email="teen@mailinator.com",
        username="teen",
        password="123123",
        studentprofile__underage=False
    )
    MentorFactory(
        email="mentor@mailinator.com",
        username="mentor",
        password="123123"
    )
    ParentFactory(
        email="parent@mailinator.com",
        username="parent",
        password="123123"
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