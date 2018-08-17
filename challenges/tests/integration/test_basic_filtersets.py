import pytest
from mock import MagicMock
from django.http import HttpResponseRedirect, Http404
from profiles.factories import *
from challenges.factories import *

from challenges.views import UnfilteredChallenges, CoreChallenges

@pytest.mark.skip(reason="reworking filtersets")
@pytest.mark.django_db
def test_unfiltered_challenges_apply(rf):
    challenges = ChallengeFactory.create_batch(5)
    request = rf.get('/challenges/')
    template_name, context, response =  UnfilteredChallenges(request).apply()
    assert template_name == None
    assert context['title'] == "All Design Challenges"
    assert set(context['challenges'].all()) == set(challenges)

@pytest.mark.skip(reason="reworking filtersets")
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

    request = rf.get('/challenges/', {"aifamilychallenge": "1"})
    assert CoreChallenges(request).requested

    request = rf.get('/challenges/', {"aifamilychallenge": "x"})
    assert CoreChallenges(request).requested

@pytest.mark.skip(reason="reworking filtersets")
@pytest.mark.django_db
def test_core_challenges_apply(rf):
    core = ChallengeFactory.create_batch(2, core=True, free=True)
    noncore = ChallengeFactory.create_batch(2, core=False, free=True)
    request = rf.get('/challenges/')
    template_name, context, response =  CoreChallenges(request).apply()
    assert template_name == None
    assert context['title'] == "AI Family Challenge"
    assert set(context['challenges'].all()) == set(core)

@pytest.mark.skip(reason="reworking filtersets")
@pytest.mark.django_db
def test_core_challenges_template_context(rf):
    core = ChallengeFactory.create_batch(1, core=True, free=True, draft=False)
    assert CoreChallenges().get_template_contexts() == [{
        "text": "AI Family Challenge",
        "full_url": "/challenges/?aifamilychallenge=1#challenges",
        "active": False
    }]

    f = CoreChallenges()
    f.apply()
    assert f.get_template_contexts() == [{
        "text": "AI Family Challenge",
        "full_url": "/challenges/?aifamilychallenge=1#challenges",
        "active": True
    }]

@pytest.mark.django_db
def test_core_challenges_template_context_empty_without_core_challenges(rf):
    assert CoreChallenges().get_template_contexts() == []
    core = ChallengeFactory.create_batch(1, core=True, free=True, draft=True)
    assert CoreChallenges().get_template_contexts() == []
