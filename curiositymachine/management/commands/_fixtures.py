from profiles.factories import *
from challenges.factories import *

def basic_users():
    UserFactory(
        email="cmadmin@mailinator.com",
        is_staff=True,
        is_superuser=True,
        username="admin",
        password="123123",
    )

    StudentFactory()
    MentorFactory()
    ParentFactory()
    EducatorFactory()

def basic_challenges():
    ChallengeFactory.create_batch(30, draft=False)

def staging():
    basic_users()
    basic_challenges()