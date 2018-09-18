import pytest
from profiles.factories import *
from rest_framework.test import APIClient
from ..factories import *

@pytest.fixture
def apiclient():
    return APIClient()

@pytest.mark.django_db
def test_list(apiclient):
    user = UserFactory(username="username", password="password")
    progress = ProgressFactory(owner=user)
    comment = CommentFactory(author=user, lesson_progress=progress, text="the text")
    other_user = UserFactory()
    other_progress = ProgressFactory(owner=other_user)

    assert apiclient.get('/lessons/comment/?lesson_progress=%s' % progress.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/comment/').status_code == 403
    assert apiclient.get('/lessons/comment/?lesson_progress=%s' % 100).status_code == 403
    assert apiclient.get('/lessons/comment/?lesson_progress=%s' % other_progress.id).status_code == 403
    assert apiclient.get('/lessons/comment/?lesson_progress=%s' % progress.id).status_code == 200
    assert len(apiclient.get('/lessons/comment/?lesson_progress=%s' % progress.id).json()) == 1
    assert apiclient.get('/lessons/comment/?lesson_progress=%s' % progress.id).json()[0]['id'] == comment.id

@pytest.mark.django_db
def test_create(apiclient):
    user = UserFactory(username="username", password="password")
    progress = ProgressFactory(owner=user)
    comment = CommentFactory(author=user, lesson_progress=progress, text="the text")
    other_user = UserFactory()
    other_progress = ProgressFactory(owner=other_user)

    data = {
        "lesson_progress": progress.id, 
        "author": user.id,
        "text": "the text",
        "upload": {}
    }
    assert apiclient.post('/lessons/comment/', data).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.post('/lessons/comment/', dict(
        data,
        lesson_progress=None
    )).status_code == 403
    assert apiclient.post('/lessons/comment/', dict(
        data,
        lesson_progress=other_progress.id
    )).status_code == 403
    assert apiclient.post('/lessons/comment/', dict(
        data,
        lesson_progress=100
    )).status_code == 403
    assert apiclient.post('/lessons/comment/', data).status_code == 201

@pytest.mark.django_db
def test_retrieve(apiclient):
    user = UserFactory(username="username", password="password")
    progress = ProgressFactory(owner=user)
    comment = CommentFactory(author=user, lesson_progress=progress, text="the text")
    other_user = UserFactory()
    other_progress = ProgressFactory(owner=other_user)
    other_comment = CommentFactory(author=other_user, lesson_progress=other_progress, text="other text")

    assert apiclient.get('/lessons/comment/%d/' % comment.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.get('/lessons/comment/%d/' % other_comment.id).status_code == 403
    assert apiclient.get('/lessons/comment/%d/' % 100).status_code == 404
    assert apiclient.get('/lessons/comment/%d/' % comment.id).status_code == 200

@pytest.mark.django_db
def test_update(apiclient):
    user = UserFactory(username="username", password="password")
    progress = ProgressFactory(owner=user)
    comment = CommentFactory(author=user, lesson_progress=progress, text="the text")
    other_user = UserFactory()
    other_progress = ProgressFactory(owner=other_user)
    other_comment = CommentFactory(author=other_user, lesson_progress=other_progress, text="other text")

    assert apiclient.patch('/lessons/comment/%d/' % comment.id, {
        "text": "new text" 
    }).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.patch('/lessons/comment/%d/' % other_comment.id, {
        "text": "new text" 
    }).status_code == 403
    assert apiclient.patch('/lessons/comment/%d/' % 100, {
        "text": "new text" 
    }).status_code == 404
    assert apiclient.patch('/lessons/comment/%d/' % comment.id, {
        "text": "new text" 
    }).status_code == 200

@pytest.mark.django_db
def test_destroy(apiclient):
    user = UserFactory(username="username", password="password")
    progress = ProgressFactory(owner=user)
    comment = CommentFactory(author=user, lesson_progress=progress, text="the text")
    other_user = UserFactory()
    other_progress = ProgressFactory(owner=other_user)
    other_comment = CommentFactory(author=other_user, lesson_progress=other_progress, text="other text")

    assert apiclient.delete('/lessons/comment/%d/' % comment.id).status_code == 302
    apiclient.login(username="username", password="password")
    assert apiclient.delete('/lessons/comment/%d/' % other_comment.id).status_code == 403
    assert apiclient.delete('/lessons/comment/%d/' % 100).status_code == 404
    assert apiclient.delete('/lessons/comment/%d/' % comment.id).status_code == 204
