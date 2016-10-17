import json, os
from django.conf import settings
from profiles.factories import *
from challenges.factories import *
from images.factories import *
from videos.factories import *

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
    # to see included app.models: 
    #   $ grep model curiositymachine/fixtures/staging.json | sort | uniq 

    with open(os.path.join(settings.BASE_DIR, 'curiositymachine/fixtures/staging.json')) as data_file:
        data = json.load(data_file)

    def lookup(lookups, k, v):
        if v and k in lookups.keys():
            lookup = lookups[k]
            if type(v) == list:
                return [lookup[pk] for pk in v]
            else:
                return lookup[v]
        return v

    def pk_map(data, model, factory, exclude=[], lookups={}):
        d = {}
        for obj in data:
            if obj['model'] == model:
                fields = {k: lookup(lookups, k, v) for k, v in obj['fields'].items() if k not in exclude}
                d[obj['pk']] = factory(**fields)
        return d

    images = pk_map(data, 'images.image', ImageFactory)
    questions = pk_map(data, 'challenges.question', QuestionFactory)
    themes = pk_map(data, 'challenges.theme', ThemeFactory)
    videos = pk_map(data, 'videos.video', VideoFactory, lookups={
        'thumbnails': images
    })
    encodeds = pk_map(data, 'videos.encodedvideo', EncodedVideoFactory, lookups={
        'video': videos
    })
    challenges = pk_map(data, 'challenges.challenge', ChallengeFactory, lookups={
        'image': images,
        'landing_image': images,
        'reflect_questions': questions,
        'themes': themes,
        'video': videos
    })
    filters = pk_map(data, 'challenges.filter', FilterFactory, lookups={
        'challenges': challenges
    })
    resources = pk_map(data, 'challenges.resource', ResourceFactory, lookups={
        'challenge': challenges
    })
    resourcefiles = pk_map(data, 'challenges.resourcefile', ResourceFileFactory, lookups={
        'resource': resources
    })

def staging():
    basic_users()
    better_challenges()