import pytest

from profiles.factories import UserFactory, ParentFactory, StudentFactory, EducatorFactory, MentorFactory

from django.core.urlresolvers import reverse

pytestmark = pytest.mark.skip(reason="Just... just no. I'll fix it later.")

@pytest.mark.django_db
def test_student_proxy_changelist_shows_only_students(client):
    students = StudentFactory.create_batch(5)
    MentorFactory.create_batch(5)
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:profiles_student_changelist"))

    assert response.status_code == 200
    assert set(response.context['cl'].queryset.all()) == set([p.profile for p in students])

@pytest.mark.django_db
def test_mentor_proxy_changelist_shows_only_mentors(client):
    mentors = MentorFactory.create_batch(5)
    StudentFactory.create_batch(5)
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:profiles_mentor_changelist"))

    assert response.status_code == 200
    assert set(response.context['cl'].queryset.all()) == set([p.profile for p in mentors])

@pytest.mark.django_db
def test_educator_proxy_changelist_shows_only_educators(client):
    educators = EducatorFactory.create_batch(5)
    StudentFactory.create_batch(5)
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:profiles_educator_changelist"))

    assert response.status_code == 200
    assert set(response.context['cl'].queryset.all()) == set([p.profile for p in educators])

@pytest.mark.django_db
def test_parent_proxy_changelist_shows_only_parents(client):
    parents = ParentFactory.create_batch(5)
    StudentFactory.create_batch(5)
    user = UserFactory(username="username", password="123123", is_staff=True, is_superuser=True, is_active=True)

    client.login(username=user.username, password="123123")
    response = client.get(reverse("admin:profiles_parent_changelist"))

    assert response.status_code == 200
    assert set(response.context['cl'].queryset.all()) == set([p.profile for p in parents])
