import pytest
import mock
from datetime import datetime
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from profiles.models import Profile, UserRole
from django.utils.timezone import now
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from profiles.tests import student, mentor, progress, challenge, loggedInMentor, STUDENT_USERNAME, STUDENT_EMAIL
from profiles import views
from profiles.factories import *
from memberships.factories import *

User = get_user_model()

@pytest.mark.django_db
def test_gets_ok(client, mentor):
    assert client.get('/join/').status_code == 200
    assert client.get('/join/some_source/').status_code == 200
    assert client.get('/join_as_mentor/').status_code == 200
    assert client.get('/join_as_mentor/source/').status_code == 200
    assert client.get('/join_as_educator/').status_code == 200
    assert client.get('/join_as_educator/source/').status_code == 200
    assert client.get('/join_as_parent/').status_code == 200
    assert client.get('/join_as_parent/source/').status_code == 200
    assert client.get('/mentors/').status_code == 200
    assert client.get('/mentors/%s/' % mentor.username).status_code == 200

@pytest.mark.django_db
def test_new_user_has_default_typeless_profile():
    user = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    assert user.profile
    assert UserRole(user.profile.role) == UserRole.none
    assert not user.profile.is_student
    assert not user.profile.is_mentor

@pytest.mark.django_db
def test_old_progress_dont_show(client, loggedInMentor, progress):
    startdate = now() - relativedelta(months=int(settings.PROGRESS_MONTH_ACTIVE_LIMIT))
    progress.started = startdate
    progress.mentor = loggedInMentor
    progress.save()

    response = client.get('/home/', follow = True)
    assert response.status_code == 200
    assert len(response.context['progresses']) == 0

@pytest.mark.django_db
def test_new_progress_will_show(client, loggedInMentor, progress):
    startdate = now()
    progress.started = startdate
    progress.mentor = loggedInMentor
    progress.save()

    response = client.get('/home/', follow = True)
    assert response.status_code == 200
    assert len(response.context['progresses']) == 1

@pytest.mark.django_db
def test_student_inactive_for_with_no_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = None
    profile.save()
    assert Profile.inactive_students().count() == 1

@pytest.mark.django_db
def test_student_inactive_for_with_last_inactive_email_sent_on(student):
    profile = student.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
    last_sent_on = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT) - 2)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_students().count() == 0


@pytest.mark.django_db
def test_mentor_inactive_for_with_no_last_inactive_email_sent_on(mentor):
    profile = mentor.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = None
    profile.save()
    assert Profile.inactive_mentors().count() == 1

@pytest.mark.django_db
def test_mentor_inactive_for_with_last_inactive_email_sent_on(mentor):
    profile = mentor.profile
    startdate = now()
    enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
    last_sent_on = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR) - 2)
    profile.last_active_on = enddate
    profile.last_inactive_email_sent_on = last_sent_on
    profile.save()
    assert Profile.inactive_mentors().count() == 0

def test_dispatch_dispatches_action_to_module(rf):
    student = User(username="student")
    student_profile = Profile(role=UserRole.student.value, birthday=datetime.now())
    student_profile.user = student

    mentor = User(username="mentor")
    mentor_profile = Profile(role=UserRole.mentor.value)
    mentor_profile.user = mentor

    request = rf.get('/path')
    with mock.patch('profiles.views.student') as studentViews, mock.patch('profiles.views.mentor') as mentorViews:
        request.user = student
        views.dispatch(request, 'foo')
        assert studentViews.foo.called
        assert not mentorViews.foo.called

        studentViews.reset_mock()
        mentorViews.reset_mock()

        request.user = mentor
        views.dispatch(request, 'foo')
        assert not studentViews.foo.called
        assert mentorViews.foo.called

def test_dispatch_passes_through_args_and_kwargs(rf):
    student = User(username="student")
    student_profile = Profile(role=UserRole.student.value, birthday=datetime.now())
    student_profile.user = student

    request = rf.get('/path')
    request.user = student
    with mock.patch('profiles.views.student') as studentViews:
        views.dispatch(request, 'foo', 'arg', kwarg=True)
        assert studentViews.foo.called
        assert studentViews.foo.call_args == mock.call(request, 'arg', kwarg=True)

def test_user_type():
    assert ProfileFactory.build(user__is_superuser=True).user_type == 'admin'
    assert ProfileFactory.build(role=UserRole.mentor.value).user_type == 'mentor'
    assert ProfileFactory.build(role=UserRole.student.value).user_type == 'student'
    assert ProfileFactory.build(role=UserRole.student.value, birthday=now()).user_type == 'underage student'
    assert ProfileFactory.build(role=UserRole.educator.value).user_type == 'educator'
    assert ProfileFactory.build(role=UserRole.parent.value).user_type == 'parent'

@pytest.mark.django_db
def test_in_active_membership():
    student = StudentFactory()
    student2 = StudentFactory()
    student3 = StudentFactory()
    MembershipFactory(members=[student])
    MembershipFactory(is_active=False, members=[student3])

    assert student.profile.in_active_membership
    assert not student2.profile.in_active_membership
    assert not student3.profile.in_active_membership

@pytest.mark.django_db
def test_should_add_email():
    student = StudentFactory(email='')
    student2 = StudentFactory(email='')
    student3 = StudentFactory(email='')
    MembershipFactory(members=[student])
    MembershipFactory(is_active=False, members=[student3])

    assert not student.profile.should_add_email
    assert student2.profile.should_add_email
    assert student3.profile.should_add_email

    student.email = 'email@email.com'
    student.save()
    student2.email = 'email@email.com'
    student2.save()
    student3.email = 'email@email.com'
    student3.save()

    assert not student.profile.should_add_email
    assert not student2.profile.should_add_email
    assert not student3.profile.should_add_email

