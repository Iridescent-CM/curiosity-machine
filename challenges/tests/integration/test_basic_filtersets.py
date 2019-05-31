import pytest
from mock import MagicMock
from django.http import HttpResponseRedirect, Http404
from profiles.factories import *
from challenges.factories import *

from challenges.views import UnfilteredChallenges

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

