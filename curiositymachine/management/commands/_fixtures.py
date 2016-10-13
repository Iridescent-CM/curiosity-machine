import json, os
from django.conf import settings
from profiles.factories import *
from challenges.factories import *
from images.factories import *

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
        profile__underage=True
    )
    StudentFactory(
        email="teen@mailinator.com",
        username="teen",
        password="123123",
        profile__underage=False
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

def better_challenges():
    # uses a `python manage.py dumpdata` json fixture as the basis for driving the factories appropriately

    with open(os.path.join(settings.BASE_DIR, 'curiositymachine/fixtures/staging.json')) as data_file:
        data = json.load(data_file)

    def pk_map(data, model, factory):
        d = {}
        for obj in data:
            if obj['model'] == model:
                d[obj['pk']] = factory(**obj['fields'])
        return d

    images = pk_map(data, 'images.image', ImageFactory)
    questions = pk_map(data, 'challenges.question', QuestionFactory)

    excluded_fields = [
        'video',
        'themes',
    ]

    def maybe_swap(k, v):
        if k in ['image', 'landing_image'] and v:
            return images[v]
        elif k == 'reflect_questions' and v:
            return [questions[pk] for pk in v]
        return v

    for obj in data:
        if obj['model'] == 'challenges.challenge':
            challenge = ChallengeFactory(**{k: maybe_swap(k, v) for k, v in obj['fields'].items() if k not in excluded_fields})

def staging():
    basic_users()
    better_challenges()