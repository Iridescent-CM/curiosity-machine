import pytest
import mock
from .views import home
from django.contrib.auth.models import User
from profiles.models import Profile
from challenges.models import Challenge, Progress
from django.utils.timezone import now
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.conf import settings
from profiles import forms

STUDENT_USERNAME = "student"
STUDENT_EMAIL = "student@example.com"
MENTOR_USERNAME = "mentor"
MENTOR_EMAIL = "mentor@example.com"

@pytest.fixture
def student():
    student = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.save()
    return student

@pytest.fixture
def mentor():
    mentor = User.objects.create(username=MENTOR_USERNAME, email=MENTOR_EMAIL)
    mentor.profile.is_mentor = True
    mentor.profile.approved = True
    mentor.profile.save()
    return mentor

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge")

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def loggedInMentor(client):
    mentor = User.objects.create_user(username='mentor2', email='mentor@example.com', password='password')
    mentor.profile.approved = True
    mentor.profile.is_mentor = True
    mentor.profile.save()
    client.login(username='mentor2', password='password')
    return mentor

@pytest.mark.django_db
def test_new_user_has_default_typeless_profile():
    user = User.objects.create(username=STUDENT_USERNAME, email=STUDENT_EMAIL)
    assert user.profile
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

def test_student_join_form_required_fields():
    f = forms.JoinForm()

    assert f.fields['username'].required
    assert f.fields['password'].required
    assert f.fields['confirm_password'].required
    assert f.fields['birthday'].required
    assert f.fields['city'].required
    
    assert not f.fields['email'].required
    assert not f.fields['picture_filepicker_url'].required
    assert not f.fields['first_name'].required
    assert not f.fields['last_name'].required
    assert not f.fields['parent_first_name'].required
    assert not f.fields['parent_last_name'].required

def test_student_join_form_clean_requires_parent():
    bday = now() - relativedelta(years=12)
    f = forms.JoinForm(data={
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert 'parent_first_name' in f.errors
    assert 'parent_last_name' in f.errors

    bday = now() - relativedelta(years=13, days=1)
    f = forms.JoinForm(data={
        'birthday_year': bday.year,
        'birthday_month': bday.month,
        'birthday_day': bday.day
    })
    assert 'parent_first_name' not in f.errors
    assert 'parent_last_name' not in f.errors

def test_student_join_form_clean_birthday_set():
    # values are widget initial values
    f = forms.JoinForm(data={
        'birthday_year': now().year,
        'birthday_month': 1,
        'birthday_day': 1
    })
    assert 'birthday' in f.errors

def test_mentor_join_form_required_fields():
    f = forms.MentorJoinForm()

    assert f.fields['username'].required
    assert f.fields['email'].required
    assert f.fields['password'].required
    assert f.fields['confirm_password'].required
    assert f.fields['city'].required
    
    assert not f.fields['birthday'].required
    assert not f.fields['picture_filepicker_url'].required
    assert not f.fields['first_name'].required
    assert not f.fields['last_name'].required
    assert not f.fields['title'].required
    assert not f.fields['employer'].required

def test_mentor_join_form_clean_ignores_birthday():
    f = forms.MentorJoinForm(data={})
    assert 'birthday' not in f.errors

def test_mentor_join_form_clean_passwords_match():
    f = forms.MentorJoinForm(data={
        'password': '123123',
        'confirm_password': '456456'
    })
    assert 'password' in f.errors
    assert 'do not match' in f.errors['password'].as_text()

def test_mentor_join_form_clean_password_strength():
    f = forms.MentorJoinForm(data={
        'password': 'hi'
    })
    assert 'password' in f.errors
    assert 'must be at least 6 characters long' in f.errors['password'].as_text()

def test_mentor_join_form_clean_username_illegal_characters():
    f = forms.MentorJoinForm(data={
        'username': 'me!'
    })
    assert 'username' in f.errors
    assert 'can only include' in f.errors['username'].as_text()

def test_mentor_edit_form_required_fields(rf):
    req = rf.get('/some/path')
    req.user = mock.Mock(wrap=User)

    f = forms.MentorProfileEditForm(request=req)

    assert f.fields['email'].required
    assert f.fields['city'].required
    
    assert not f.fields['password'].required
    assert not f.fields['confirm_password'].required
    assert not f.fields['birthday'].required
    assert not f.fields['picture_filepicker_url'].required
    assert not f.fields['first_name'].required
    assert not f.fields['last_name'].required
    assert not f.fields['title'].required
    assert not f.fields['employer'].required
    assert not f.fields['about_me'].required
    assert not f.fields['about_me_filepicker_url'].required
    assert not f.fields['about_research'].required
    assert not f.fields['about_research_filepicker_url'].required
