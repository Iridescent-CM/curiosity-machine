import pytest
from mock import MagicMock
from django.http import HttpResponseRedirect, Http404
from profiles.factories import *
from challenges.factories import *

from challenges.views import FilterChallenges

def test_not_requested(rf):
    request = rf.get('/challenges/')
    assert not FilterChallenges(request).requested

    request = rf.get('/challenges/', {"other": "2"})
    assert not FilterChallenges(request).requested

def test_requested(rf):
    request = rf.get('/challenges/', {"filter_id": "2"})
    assert FilterChallenges(request).requested

    request = rf.get('/challenges/', {"filter_id": 'bad_value'})
    assert FilterChallenges(request).requested

@pytest.mark.django_db
def test_apply_404s_on_bad_query_param(rf):
    request = rf.get('/challenges/', {"filter_id": "x"})

    with pytest.raises(Http404):
        FilterChallenges(request).apply()

@pytest.mark.django_db
def test_apply_404s_on_missing_filter(rf):
    request = rf.get('/challenges/', {"filter_id": "2"})

    with pytest.raises(Http404):
        FilterChallenges(request).apply()

@pytest.mark.django_db
def test_apply_successful(rf):
    challenges = ChallengeFactory.create_batch(3)
    filt = FilterFactory(name="Filter", challenges=challenges[:2])

    request = rf.get('/challenges/', {"filter_id": filt.id})

    f = FilterChallenges(request)
    template_name, context, response = f.apply()
    assert template_name == None
    assert context['title'] == "Filter Design Challenges"
    assert set(context['challenges'].all()) == set(challenges[:2])

@pytest.mark.django_db
def test_builds_template_context(rf):
    filter1 = FilterFactory(name="Filter1")
    filter2 = FilterFactory(name="Filter2")
    filter3 = FilterFactory(name="Filter2", visible=False)

    request = rf.get('/challenges/', {"filter_id": filter1.id})

    f = FilterChallenges(request)
    f.apply()
    assert f.get_template_contexts() == [
        {
            "text": "Filter1",
            "active": True,
            "full_url": "/challenges/?filter_id=%d#challenges" % filter1.id
        },
        {
            "text": "Filter2",
            "active": False,
            "full_url": "/challenges/?filter_id=%d#challenges" % filter2.id
        }
    ]
