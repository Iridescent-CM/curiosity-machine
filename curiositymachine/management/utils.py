import json
from django.utils.timezone import now
from hellosign.models import SignatureStatus
from profiles.models import UserRole
from surveys.models import ResponseStatus

from challenges.factories import *
from cmcomments.factories import *
from educators.factories import *
from families.factories import *
from hellosign.factories import *
from images.factories import *
from locations.factories import *
from memberships.factories import *
from mentors.factories import *
from parents.factories import *
from profiles.factories import *
from students.factories import *
from surveys.factories import *
from units.factories import *
from videos.factories import *

def lookup(lookups, k, v):
    """
    Looks up an object by pk in a dictionary of pk_map dictionaries.
    Trivially returns v when k is not a key in lookups.

    Intended use: when the fixture data for Model specifies a field like
    "someothermodel": 1, we might need to look up a SomeOtherModel of pk 1
    which has been previously built from the same fixture data in order to
    build a complete Model. This lets us do that, or trivially hands back
    the original value if the field name has not been indicated as something
    that needs looking up.

    lookups: dictionary mapping field names to pk_map dictionaries containing
             previously instantiated objects
    k:  the field name
    v:  the pk
    """
    if v and k in lookups.keys():
        lookup = lookups[k]
        if type(v) == list:
            return [lookup[pk] for pk in v]
        else:
            return lookup[v]
    return v

def pk_map(data, model, factory, exclude=[], lookups={}, force={}, build=False):
    """
    Given json fixture data, this filters for a specific model
    and attempts to instantiate with the specified factory.

    Returns a dictionary mapping pks to the instantiated object.

    Fields can be excluded from the factory arguments with the exclude parameter.

    Lookups is a dictionary of field names specifying related objects and the dictionaries
    created by prior calls to pk_map for those models.

    You can force fields to contain a certain value with the force parameter.

    Build lets you specify that the factory should build, not create.
    """
    d = {}
    for obj in data:
        if obj['model'] == model:
            fields = {k: lookup(lookups, k, v) for k, v in obj['fields'].items() if k not in exclude}
            fields.update(force)
            if build:
                d[obj['pk']] = factory.build(**fields)
            else:
                d[obj['pk']] = factory(**fields)
    return d

def load_fixture(f):
    """
    Uses a `python manage.py dumpdata` json fixture as the basis for driving factories to
    appropriately install the fixture data.

    To see included app.models in a fixture:
      $ grep model curiositymachine/fixtures/staging.json | sort | uniq

    Order matters! Create "leaf" models first, or alternatively use the build parameter and
    handle model saving yourself after assembling related models together.
    """

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

    locations = pk_map(data, 'locations.location', LocationFactory)
    users = pk_map(data, 'auth.user', UserFactory, exclude=['groups', 'user_permissions', 'password'], build=True)
    studentprofiles = pk_map(data, 'students.studentprofile', StudentProfileFactory, lookups={
        'user': users,
        'image': images,
    }, build=True)
    educatorprofiles = pk_map(data, 'educators.educatorprofile', EducatorProfileFactory, lookups={
        'user': users,
        'image': images,
        'location': locations,
    }, build=True)
    familyprofiles = pk_map(data, 'families.familyprofile', FamilyProfileFactory, lookups={
        'user': users,
        'image': images,
        'location': locations,
    }, build=True)
    parentprofiles = pk_map(data, 'parents.parentprofile', ParentProfileFactory, lookups={
        'user': users,
        'image': images,
    }, build=True)
    mentorprofiles = pk_map(data, 'mentors.mentorprofile', MentorProfileFactory, lookups={
        'user': users,
        'image': images,
    }, build=True)
    extras = pk_map(data, 'profiles.userextra', UserExtraFactory, lookups={
        'user': users,
    }, build=True)
    for user in users.values():
        user.save()
        user.extra.user = user # i hate this so much
        user.extra.save()
        role = UserRole(user.extra.role)
        if role.profile_attr:
            profile = getattr(user, role.profile_attr)
            profile.user = user
            profile.save()

    familymembers = pk_map(data, 'families.familymember', FamilyMemberFactory, lookups={
        'account': users,
        'image': images,
    })

    units = pk_map(data, 'units.unit', UnitFactory, lookups={
        'image': images,
        'standards_alignment_image': images,
    })

    memberships = pk_map(data, 'memberships.membership', MembershipFactory, lookups={
        'challenges': challenges,
        'units': units,
    })
    members = pk_map(data, 'memberships.member', MemberFactory, lookups={
        'membership': memberships,
        'user': users
    })

    surveys = pk_map(
        data,
        'surveys.surveyresponse',
        SurveyResponseFactory,
        lookups={
            'user': users,
        },
        force={
            'status': ResponseStatus.COMPLETED
        }
    )
    signatures = pk_map(
        data,
        'hellosign.signature',
        SignatureFactory,
        lookups={
            'user': users,
        },
        force={
            'status': SignatureStatus.SIGNED,
        }
    )

    progresses = pk_map(
        data,
        'challenges.progress',
        ProgressFactory,
        lookups={
            'challenge': challenges,
            'owner': users,
            'mentor': users
        },
        force={
            'started': now(),
        }
    )
    comments = pk_map(data, 'cmcomments.comment', CommentFactory, lookups={
        'challenge_progress': progresses,
        'user': users,
        'image': images,
        'video': videos,
    })
