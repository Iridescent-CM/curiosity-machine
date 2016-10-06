import pytest
from mock import MagicMock
from django.http import HttpResponseRedirect, Http404
from profiles.factories import *
from challenges.factories import *

from challenges.views import UnfilteredChallenges, CoreChallenges

@pytest.mark.django_db
def test_unfiltered_challenges_apply(rf):
    challenges = ChallengeFactory.create_batch(5)
    request = rf.get('/challenges/')
    title, qs, response =  UnfilteredChallenges(request).apply()
    assert title == "All Design Challenges"
    assert set(qs.all()) == set(challenges)

def test_unfiltered_challenges_template_context(rf):
    assert UnfilteredChallenges().get_template_contexts() == [{
        "text": "All Challenges",
        "full_url": "/challenges/#challenges",
        "active": False
    }]

    f = UnfilteredChallenges()
    f.apply()
    assert f.get_template_contexts() == [{
        "text": "All Challenges",
        "full_url": "/challenges/#challenges",
        "active": True
    }]

def test_core_challenges_requested(rf):
    request = rf.get('/challenges/')
    assert not CoreChallenges(request).requested

    request = rf.get('/challenges/', {"free": "1"})
    assert CoreChallenges(request).requested

    request = rf.get('/challenges/', {"free": "x"})
    assert CoreChallenges(request).requested

@pytest.mark.django_db
def test_core_challenges_apply(rf):
    core = ChallengeFactory.create_batch(2, core=True, free=True)
    noncore = ChallengeFactory.create_batch(2, core=False, free=True)
    request = rf.get('/challenges/')
    title, qs, response =  CoreChallenges(request).apply()
    assert title == "Free Design Challenges"
    assert set(qs.all()) == set(core)

@pytest.mark.django_db
def test_core_challenges_template_context(rf):
    assert CoreChallenges().get_template_contexts() == [{
        "text": "Free Challenges",
        "full_url": "/challenges/?free=1#challenges",
        "active": False
    }]

    f = CoreChallenges()
    f.apply()
    assert f.get_template_contexts() == [{
        "text": "Free Challenges",
        "full_url": "/challenges/?free=1#challenges",
        "active": True
    }]
