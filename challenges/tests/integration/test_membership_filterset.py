import pytest
from mock import MagicMock
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponseRedirect
from profiles.factories import *
from memberships.factories import *
from challenges.factories import *

from challenges.views import MembershipChallenges

def test_not_requested(rf):
    request = rf.get('/challenges/')
    assert not MembershipChallenges(request).requested

    request = rf.get('/challenges/', {"other": 2})
    assert not MembershipChallenges(request).requested

def test_requested(rf):
    request = rf.get('/challenges/', {"membership": 2})
    assert MembershipChallenges(request).requested

    request = rf.get('/challenges/', {"membership": 'bad_value'})
    assert MembershipChallenges(request).requested

def test_apply_when_anonymous(rf):
    request = rf.get('/challenges/', {"membership": 2})
    request.user = AnonymousUser()

    f = MembershipChallenges(request)
    template_name, context, response = f.apply()
    assert type(response) == HttpResponseRedirect
    assert "next=" in response.url

@pytest.mark.django_db
def test_apply_on_inaccessible_memberships(rf):
    membership = MembershipFactory()

    request = rf.get('/challenges/', {"membership": membership.id})
    request.user = UserFactory()
    request._messages = MagicMock()

    f = MembershipChallenges(request)
    template_name, context, response = f.apply()
    assert type(response) == HttpResponseRedirect
    assert request._messages.add.called

    request = rf.get('/challenges/', {"membership": membership.id + 1})
    request.user = UserFactory()
    request._messages = MagicMock()

    f = MembershipChallenges(request)
    template_name, context, response = f.apply()
    assert type(response) == HttpResponseRedirect
    assert request._messages.add.called

@pytest.mark.django_db
def test_apply_on_inactive_memberships(rf):
    membership = MembershipFactory(is_active=False)

    request = rf.get('/challenges/', {"membership": membership.id})
    request.user = UserFactory()
    request._messages = MagicMock()

    f = MembershipChallenges(request)
    template_name, context, response = f.apply()
    assert type(response) == HttpResponseRedirect
    assert request._messages.add.called

@pytest.mark.django_db
def test_apply_successful(rf):
    user = UserFactory()
    challenges = ChallengeFactory.create_batch(3)
    membership = MembershipFactory(members=[user], display_name="Membership", challenges=challenges[:2])

    request = rf.get('/challenges/', {"membership": membership.id})
    request.user = user
    request._messages = MagicMock()

    f = MembershipChallenges(request)
    template_name, context, response = f.apply()
    assert template_name == None
    assert context['title'] == "Membership Design Challenges"
    assert set(context['challenges'].all()) == set(challenges[:2])

@pytest.mark.django_db
def test_builds_template_context(rf):
    user = UserFactory()
    membership1 = MembershipFactory(members=[user], display_name="Membership1")
    membership2 = MembershipFactory(members=[user], display_name="Membership2")
    membership3 = MembershipFactory()

    request = rf.get('/challenges/', {"membership": membership2.id})
    request.user = user
    request._messages = MagicMock()

    f = MembershipChallenges(request)
    f.apply()
    assert f.get_template_contexts() == [
        {
            "text": "Membership1",
            "active": False,
            "full_url": "/challenges/?membership=%d#challenges" % membership1.id
        },
        {
            "text": "Membership2",
            "active": True,
            "full_url": "/challenges/?membership=%d#challenges" % membership2.id
        }
    ]

@pytest.mark.django_db
def test_template_context_skips_inactive(rf):
    user = UserFactory()
    membership1 = MembershipFactory(members=[user], is_active=False)

    request = rf.get('/challenges/')
    request.user = user
    request._messages = MagicMock()

    f = MembershipChallenges(request)
    assert f.get_template_contexts() == []
