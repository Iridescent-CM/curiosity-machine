import json
from challenges.factories import *
from cmcomments.factories import *
from images.factories import *
from memberships.factories import *
from profiles.factories import *
from videos.factories import *

def lookup(lookups, k, v):
    if v and k in lookups.keys():
        lookup = lookups[k]
        if type(v) == list:
            return [lookup[pk] for pk in v]
        else:
            return lookup[v]
    return v

def pk_map(data, model, factory, exclude=[], lookups={}, build=False):
    d = {}
    for obj in data:
        if obj['model'] == model:
            fields = {k: lookup(lookups, k, v) for k, v in obj['fields'].items() if k not in exclude}
            if build:
                d[obj['pk']] = factory.build(**fields)
            else:
                d[obj['pk']] = factory(**fields)
    return d

def load_fixture(f):
    # uses a `python manage.py dumpdata` json fixture as the basis for driving the factories appropriately
    # to see included app.models in a fixture: 
    #   $ grep model curiositymachine/fixtures/staging.json | sort | uniq 

    with open(f) as data_file:
        data = json.load(data_file)

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

    users = pk_map(data, 'auth.user', UserFactory, exclude=['groups', 'user_permissions', 'password'], build=True)
    profiles = pk_map(data, 'profiles.profile', ProfileFactory, lookups={
        'user': users,     
        'image': images,
    }, build=True)
    for user in users.values():
        user.save()
        user.profile.user = user # i hate this so much
        user.profile.save()

    memberships = pk_map(data, 'memberships.membership', MembershipFactory, lookups={
        'challenges': challenges    
    })
    members = pk_map(data, 'memberships.member', MemberFactory, lookups={
        'membership': memberships,
        'user': users
    })

    progresses = pk_map(data, 'challenges.progress', ProgressFactory, lookups={
        'challenge': challenges,
        'student': users,
        'mentor': users
    })
    comments = pk_map(data, 'cmcomments.comment', CommentFactory, lookups={
        'challenge_progress': progresses,
        'user': users,
        'image': images,
        'video': videos,
    })
