import pytest
from .models import Module, Comment
from .views import module as module_view
from .views import comments
from profiles.tests import student, mentor

@pytest.fixture
def module():
    return Module.objects.create(id=1)

@pytest.fixture
def training_comment(module, mentor):
    return module.comments.create(user=mentor)

@pytest.mark.django_db
def test_module_response_code(rf, student, mentor, module):
    request = rf.get('/training/1/')
    request.user = student
    response = module_view(request, module.id)
    assert response.status_code == 403

    request = rf.get('/training/1/')
    request.user = mentor
    response = module_view(request, module.id)
    assert response.status_code == 200

    mentor.profile.approved = False
    request = rf.get('/training/1/')
    request.user = mentor
    response = module_view(request, module.id)
    assert response.status_code == 200

@pytest.mark.django_db
def test_comments_blocks_student(rf, student, mentor, module):
    request = rf.post('/training/1/1/', {'text': 'test_text'})
    request.user = student
    response = comments(request, module.id)
    assert response.status_code == 403

@pytest.mark.django_db
def test_comments_top_level(rf, student, mentor, module):
    assert Comment.objects.count() == 0
    request = rf.post('/training/1/comments/', {'text': 'test_text'})
    request.user = mentor
    response = comments(request, module.id)
    assert response.status_code == 204
    assert Comment.objects.count() == 1
    comment = Comment.objects.first()
    assert comment.text == 'test_text'
    assert not comment.thread_id

@pytest.mark.django_db
def test_comments_with_thread_id(rf, student, mentor, module, training_comment):
    assert Comment.objects.count() == 1
    request = rf.post('/training/1/comments/1/', {'text': 'test_text'})
    request.user = mentor
    response = comments(request, module.id, training_comment.id)
    assert response.status_code == 204
    assert Comment.objects.count() == 2
    comment = Comment.objects.first()
    assert comment.text == 'test_text'
    assert comment.thread_id == training_comment.id
