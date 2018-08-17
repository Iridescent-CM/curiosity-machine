import pytest
from mock import MagicMock
from django.http import HttpResponseRedirect, Http404
from profiles.factories import *
from challenges.factories import *

from challenges.views import ThemeChallenges

def test_not_requested(rf):
    request = rf.get('/challenges/')
    assert not ThemeChallenges(request).requested

    request = rf.get('/challenges/', {"other": "x"})
    assert not ThemeChallenges(request).requested

def test_requested(rf):
    request = rf.get('/challenges/', {"theme": "x"})
    assert ThemeChallenges(request).requested

@pytest.mark.skip(reason="reworking filtersets")
@pytest.mark.django_db
def test_apply_successful(rf):
    challenges = ChallengeFactory.create_batch(3)
    theme = ThemeFactory(challenges=challenges[:2], name="theme")

    request = rf.get('/challenges/', {"theme": theme.name})

    f = ThemeChallenges(request)
    template_name, context, response = f.apply()
    assert template_name == None
    assert context['title'] == "theme Design Challenges"
    assert set(context['challenges'].all()) == set(challenges[:2])

@pytest.mark.skip(reason="reworking filtersets")
@pytest.mark.django_db
def test_builds_template_context(rf):
    theme1 = ThemeFactory(name="theme1", icon="icon-theme1")
    theme2 = ThemeFactory(name="theme2", icon="icon-theme2")

    request = rf.get('/challenges/', {"theme": "theme1"})

    f = ThemeChallenges(request)
    f.apply()
    assert f.get_template_contexts() == [
        {
            "text": '<i class="icon icon-theme1"></i> theme1',
            "active": True,
            "full_url": "/challenges/?theme=%s#challenges" % theme1.name
        },
        {
            "text": '<i class="icon icon-theme2"></i> theme2',
            "active": False,
            "full_url": "/challenges/?theme=%s#challenges" % theme2.name
        }
    ]
