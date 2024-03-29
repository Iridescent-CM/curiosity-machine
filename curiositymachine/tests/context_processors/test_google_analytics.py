import pytest
import mock
from django.contrib.auth.models import AnonymousUser
from educators.factories import *
from families.factories import *
from memberships.factories import *
from memberships.models import *
from profiles.factories import *
from students.factories import *
from ...context_processors import google_analytics
from ...context_processors.google_analytics import add_event

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

class TestEvents:
    def test_add_event_puts_events_in_context(self, rf):
        request = rf.get('/')
        request.user = AnonymousUser()
        request.session = {}

        add_event(request, 'cat', 'act', 'lab')
        add_event(request, 'cat2', 'act2', 'lab2')

        context = google_analytics(request)

        events = context["ga_events"]()
        assert len(events) == 2
        assert {'category': 'cat', 'action':'act', 'label':'lab'} in events
        assert {'category': 'cat2', 'action':'act2', 'label':'lab2'} in events

class TestUserType:
    def test_anonymous_marked_as_anonymous(self, rf):
        user = mock.Mock()
        user.is_authenticated = False

        request = rf.get('/')
        request.user = user
        request.session = {}

        context = google_analytics(request)
        assert context["ga_dimension_user_type"] == "Anonymous"

    def test_staff_marked_as_staff(self, rf):
        user = mock.Mock()
        user.is_authenticated = True
        user.is_staff = True
        user.membership_set = Membership.objects.none()

        request = rf.get('/')
        request.user = user
        request.session = {}

        context = google_analytics(request)
        assert context["ga_dimension_user_type"] == "Staff"

    def test_other_roles_marked_as_capitalized_role(self, rf):
        user = mock.Mock()
        user.is_authenticated = True
        user.is_staff = False
        user.membership_set = Membership.objects.none()
        user.extra.role_name = "whatever"

        request = rf.get('/')
        request.user = user
        request.session = {}

        context = google_analytics(request)
        assert context["ga_dimension_user_type"] == "Whatever"