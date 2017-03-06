import pytest

from django.contrib.auth.models import AnonymousUser
from profiles.factories import *
from memberships.factories import *

from ...context_processors import google_analytics

class TestContentGrouping:
    @pytest.mark.django_db
    def test_no_grouping_without_membership(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        context = google_analytics(request)
        assert not context["ga_membership_grouping"]

        request = rf.get('/')
        request.user = StudentFactory()
        context = google_analytics(request)
        assert not context["ga_membership_grouping"]

    @pytest.mark.django_db
    def test_single_membership(self, rf):
        student = StudentFactory()
        membership = MembershipFactory(members=[student])

        request = rf.get('/')
        request.user = student
        context = google_analytics(request)
        assert context["ga_membership_grouping"] == str(membership.id)

    @pytest.mark.django_db
    def test_multi_membership(self, rf):
        student = StudentFactory()
        membership = MembershipFactory(members=[student])
        membership2 = MembershipFactory(members=[student])

        request = rf.get('/')
        request.user = student
        context = google_analytics(request)
        assert context["ga_membership_grouping"] == str(membership.id) + "-" + str(membership2.id)

    @pytest.mark.django_db
    def test_active_membership_only(self, rf):
        student = StudentFactory()
        membership = MembershipFactory(members=[student], is_active=False)

        request = rf.get('/')
        request.user = student
        context = google_analytics(request)
        assert not context["ga_membership_grouping"]

class TestFreeUserDimension:
    @pytest.mark.django_db
    def test_anonymous_user_not_counted(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        context = google_analytics(request)
        assert context["ga_dimension_free_user"] == None

    @pytest.mark.django_db
    def test_no_membership(self, rf):
        request = rf.get('/')
        request.user = StudentFactory()
        context = google_analytics(request)
        assert context["ga_dimension_free_user"] == "Free"

    @pytest.mark.django_db
    def test_inactive_membership(self, rf):
        student = StudentFactory()
        membership = MembershipFactory(members=[student], is_active=False)

        request = rf.get('/')
        request.user = student
        context = google_analytics(request)
        assert context["ga_dimension_free_user"] == "Free"

    @pytest.mark.django_db
    def test_active_membership(self, rf):
        student = StudentFactory()
        membership = MembershipFactory(members=[student], is_active=True)

        request = rf.get('/')
        request.user = student
        context = google_analytics(request)
        assert context["ga_dimension_free_user"] == "Membership"