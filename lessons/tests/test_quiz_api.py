import pytest
from profiles.factories import *
from rest_framework.test import APIClient
from ..factories import *

@pytest.fixture
def apiclient():
    return APIClient()

@pytest.mark.django_db
def test_retrieve_untaken(apiclient):
    user = UserFactory(username="username", password="password")
    quiz = QuizFactory()
    assert apiclient.get('/lessons/quiz/%d/' % quiz.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/quiz/%d/' % quiz.id).status_code == 200
    assert not apiclient.get('/lessons/quiz/%d/' % quiz.id).json()['answered']
    assert apiclient.get('/lessons/quiz/%d/?taker=%d' % (quiz.id, user.id)).status_code == 200
    assert not apiclient.get('/lessons/quiz/%d/?taker=%d' % (quiz.id, user.id)).json()['answered']

@pytest.mark.django_db
def test_retrieve_taken(apiclient):
    user = UserFactory(username="username", password="password")
    quiz = QuizFactory()
    result = QuizResultFactory(taker=user, quiz=quiz)
    assert apiclient.get('/lessons/quiz/%d/' % quiz.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/quiz/%d/?taker=%d' % (quiz.id, user.id)).status_code == 200
    assert apiclient.get('/lessons/quiz/%d/?taker=%d' % (quiz.id, user.id)).json()['answered']