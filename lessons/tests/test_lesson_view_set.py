import pytest
from profiles.factories import *
from rest_framework.test import APIClient
from ..factories import *

@pytest.fixture
def apiclient():
    return APIClient()

@pytest.mark.django_db
def test_retrieve(apiclient):
    user = UserFactory(username="username", password="password")
    lesson = LessonFactory(draft=False)

    assert apiclient.get('/lessons/lesson/%d/' % lesson.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/lesson/%d/' % lesson.id).status_code == 200
    assert apiclient.get('/lessons/lesson/%d/' % 100).status_code == 404

@pytest.mark.django_db
def test_list(apiclient):
    user = UserFactory(username="username", password="password")

    assert apiclient.get('/lessons/').status_code == 200
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/').status_code == 200