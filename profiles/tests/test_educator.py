import pytest
import mock
from profiles import forms, models, views
from images.models import Image
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from curiositymachine import signals
from profiles.factories import *
from memberships.factories import MembershipFactory
from challenges.factories import *
from units.factories import *

User = get_user_model()

def test_form_required_fields_on_creation():
    f = forms.educator.EducatorUserAndProfileForm()

    required = ['username', 'email', 'password', 'confirm_password', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_form_required_fields_on_edit():
    user = User()
    profile = models.Profile()
    profile.user = user
    f = forms.educator.EducatorUserAndProfileForm(instance=user)

    required = ['email', 'city']
    for name, field in f.fields.items():
        if name in required:
            assert field.required, "%s should be required and isn't" % name
            required.remove(name)
        else:
            assert not field.required, "%s should not be required and is" % name

    assert len(required) == 0, "required fields %s not in form" % ",".join(required)

def test_form_validates_password_length():
    errors = forms.educator.EducatorUserAndProfileForm({
        'password': 'abc'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert "must be at least" in str(errors['password'])

@pytest.mark.django_db
def test_form_checks_password_confirmation():
    errors = forms.educator.EducatorUserAndProfileForm({
        'password': 'abc123',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' not in errors.keys()
    assert 'confirm_password' not in errors.keys()
    assert '__all__' not in errors.keys()

    errors = forms.educator.EducatorUserAndProfileForm({
        'password': 'xxxxxx',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert 'do not match' in str(errors['password'])

@pytest.mark.django_db
def test_form_validates_username():
    f = forms.educator.EducatorUserAndProfileForm({
        'username': 'user!'
    })
    assert 'username' in f.errors.as_data().keys()
    assert "can only include" in str(f.errors['username'])

@pytest.mark.django_db
def test_form_checks_username_uniqueness():
    User.objects.create(
        username='newuser',
        email='newuser@example.com',
        password='mypassword'
    )
    f = forms.educator.EducatorUserAndProfileForm({
        'username': 'newuser'
    })
    assert 'username' in f.errors.as_data().keys()
    assert "already exists" in str(f.errors['username'])

@pytest.mark.django_db
def test_creates_user_with_profile():
    f = forms.educator.EducatorUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    assert f.is_valid()
    user = f.save()
    assert hasattr(user, "profile")
    assert User.objects.all().count() == 1
    assert models.Profile.objects.all().count() == 1

@pytest.mark.django_db
def test_modifies_exisiting_user_and_profile():
    f = forms.educator.EducatorUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity',
    })
    user = f.save()
    f = forms.educator.EducatorUserAndProfileForm(
        instance=user,
        data={
            'email': 'new@example.com',
            'city': 'newcity'
        }
    )
    user = f.save()
    assert user.email == 'new@example.com'
    assert user.profile.city == 'newcity'
    assert User.objects.all().count() == 1
    assert models.Profile.objects.all().count() == 1

@pytest.mark.django_db
def test_sets_educator_role():
    f = forms.educator.EducatorUserAndProfileForm(data={
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    user = f.save()
    assert user.profile.is_educator

def test_form_checks_password_confirmation():
    errors = forms.educator.EducatorUserAndProfileForm({
        'password': 'abc123',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' not in errors.keys()
    assert 'confirm_password' not in errors.keys()
    assert '__all__' not in errors.keys()

    errors = forms.educator.EducatorUserAndProfileForm({
        'password': 'xxxxxx',
        'confirm_password': 'abc123'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert 'do not match' in str(errors['password'])

    errors = forms.educator.EducatorUserAndProfileForm({
        'password': 'abc123'
    }).errors.as_data()
    assert 'password' in errors.keys()
    assert 'do not match' in str(errors['password'])

@pytest.mark.django_db
def test_educator_profile_change_form_creates_image_from_image_url():
    f = forms.educator.EducatorUserAndProfileForm({
        'image_url_url': "http://example.com/",
        'password': '123123',
        'confirm_password': '123123',
        'username': 'example',
        'email': 'email@example.com',
        'city': 'mycity'
    })
    user = f.save(commit=False)
    assert type(user.profile.image) == Image
    assert user.profile.image.source_url == 'http://example.com/'

@pytest.mark.django_db
def test_join_sends_signal(rf):
    handler = mock.MagicMock()
    signal = signals.created_account
    signal.connect(handler)

    request = rf.post('/join_as_educator', data={
        'educator-username': 'user',
        'educator-email': 'email@example.com',
        'educator-password': '123123',
        'educator-confirm_password': '123123',
        'educator-city': 'city'
    })
    request.session = mock.MagicMock()
    response = views.educator.join(request)

    handler.assert_called_once()

@pytest.mark.django_db
def test_join(rf):
    request = rf.post('/join_as_educator', data={
        'educator-username': 'user',
        'educator-email': 'email@example.com',
        'educator-password': '123123',
        'educator-confirm_password': '123123',
        'educator-city': 'city'
    })
    request.session = mock.MagicMock()
    request.user = AnonymousUser()
    response = views.educator.join(request)
    assert response.status_code == 302
    assert User.objects.filter(username='user').count() == 1

@pytest.mark.django_db
def test_educator_dashboard_guides_page_context_has_units(client):
    units = UnitFactory.create_batch(5, listed=False)
    listed_units = UnitFactory.create_batch(5, listed=True)
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get("/home/guides", follow=True)
    assert set(response.context["units"]) == set(listed_units)

@pytest.mark.django_db
def test_educator_dashboard_guides_page_context_has_extra_units(client):
    units = UnitFactory.create_batch(5, listed=False)
    educator = EducatorFactory(username="edu", password="123123")
    membership = MembershipFactory(members=[educator], extra_units=units)

    client.login(username="edu", password="123123")
    response = client.get("/home/guides", follow=True)
    assert set(response.context["extra_units"]) == set(units)
    assert response.context["membership"] == membership

@pytest.mark.django_db
def test_educator_dashboard_challenges_page_context_has_core_challenges(client):
    challenges = ChallengeFactory.create_batch(3, draft=False)
    core_challenges = ChallengeFactory.create_batch(3, core=True, free=True, draft=False)
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get("/home", follow=True)
    assert set(response.context["core_challenges"]) == set(core_challenges)

@pytest.mark.django_db
def test_educator_dashboard_challenges_page_context_has_membership_challenges(client):
    challenges = ChallengeFactory.create_batch(3, draft=False)
    educator = EducatorFactory(username="edu", password="123123")
    membership = MembershipFactory(members=[educator], challenges=challenges)

    client.login(username="edu", password="123123")
    response = client.get("/home", follow=True)
    assert set(response.context["membership_challenges"]) == set(challenges)
    assert response.context["membership"] == membership

@pytest.mark.django_db
def test_educator_dashboard_student_detail_page_context_has_connected_student(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    membership = MembershipFactory(members=[educator, student])

    client.login(username="edu", password="123123")
    response = client.get("/home/students/%d/" % student.id, follow=True)
    assert response.context["student"] == student

@pytest.mark.xfail(reason="not yet implemented")
@pytest.mark.django_db
def test_educator_dashboard_student_detail_page_context_404s_on_non_connected_student(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")

    client.login(username="edu", password="123123")
    response = client.get("/home/students/%d/" % student.id, follow=True)
    assert response.status_code == 404

@pytest.mark.django_db
def test_educator_dashboard_students_page_context_has_no_students(client):
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get("/home/students/", follow=True)
    assert response.context["students"] == []

@pytest.mark.django_db
def test_educator_dashboard_students_page_context_has_membership_students(client):
    educator = EducatorFactory(username="edu", password="123123")
    other_educators = EducatorFactory.create_batch(4)
    students = StudentFactory.create_batch(10)
    membership = MembershipFactory(members=[educator] + other_educators + students)

    client.login(username="edu", password="123123")
    response = client.get("/home/students/", follow=True)
    assert response.context["membership"] == membership
    assert set(response.context["students"]) == set(students)

@pytest.mark.django_db
def test_educator_dashboard_page_contexts_have_membership_selection_helper(client):
    educator = EducatorFactory(username="edu", password="123123")
    memberships = [MembershipFactory(members=[educator]), MembershipFactory(members=[educator])]

    client.login(username="edu", password="123123")
    for url in ["/home", "/home/students", "/home/guides"]:
        response = client.get(url, follow=True)
        assert "membership_selection" in response.context
