import pytest
from profiles.factories import *
from rest_framework.test import APIClient
from ..factories import *
from .. models import *

@pytest.fixture
def apiclient():
    return APIClient()

@pytest.mark.django_db
def test_retrieve(apiclient):
    user = UserFactory(username="username", password="password")
    progress = ProgressFactory(owner=user)
    other_user = UserFactory()
    other_progress = ProgressFactory(owner=other_user)

    assert apiclient.get('/lessons/lesson_progress/%d/' % progress.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/lesson_progress/%d/' % other_progress.id).status_code == 403
    assert apiclient.get('/lessons/lesson_progress/%d/' % 100).status_code == 404
    assert apiclient.get('/lessons/lesson_progress/%d/' % progress.id).status_code == 200

@pytest.mark.django_db
def test_find_or_create(apiclient):
    user = UserFactory(username="username", password="password")
    lesson = LessonFactory()

    assert apiclient.get('/lessons/lesson_progress/find_or_create/').status_code == 302
    assert apiclient.get('/lessons/lesson_progress/find_or_create/?lesson=%d' % lesson.id).status_code == 302
    assert not Progress.objects.filter(owner=user, lesson=lesson).exists()

    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/lesson_progress/find_or_create/').status_code == 404
    assert not Progress.objects.filter(owner=user, lesson=lesson).exists()

    assert apiclient.get('/lessons/lesson_progress/find_or_create/?lesson=%d' % lesson.id).status_code == 302
    assert apiclient.get('/lessons/lesson_progress/find_or_create/?lesson=%d' % lesson.id).url.startswith('/lessons/lesson_progress/')
    assert Progress.objects.filter(owner=user, lesson=lesson).exists()

    assert (apiclient.get('/lessons/lesson_progress/find_or_create/?lesson=%d' % lesson.id).url ==
        apiclient.get('/lessons/lesson_progress/find_or_create/?lesson=%d' % lesson.id).url)
    assert Progress.objects.filter(owner=user, lesson=lesson).count() == 1