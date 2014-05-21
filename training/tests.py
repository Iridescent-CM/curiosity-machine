import pytest
from .models import Module, Comment
from .views import module as module_view
from .views import comments
from profiles.tests import student, mentor
from django.contrib.auth.models import User

NEW_MENTOR_USERNAME = "newbie"
NEW_MENTOR_EMAIL = "newbie@example.com"

@pytest.fixture
def new_mentor(): # not approved
    mentor = User.objects.create(username=NEW_MENTOR_USERNAME, email=NEW_MENTOR_EMAIL)
    mentor.profile.is_mentor = True
    mentor.profile.save()
    return mentor

@pytest.fixture
def module():
    return Module.objects.create(id=1)

@pytest.fixture
def module2():
    return Module.objects.create(id=2)

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
def test_comments_top_level(rf, student, new_mentor, module):
    assert Comment.objects.count() == 0
    request = rf.post('/training/1/comments/', {'text': 'test_text'})
    request.user = new_mentor
    response = comments(request, module.id)
    assert response.status_code == 302
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
    assert response.status_code == 302
    assert Comment.objects.count() == 2
    comment = Comment.objects.last()
    assert comment.text == 'test_text'
    assert comment.thread_id == training_comment.id

@pytest.mark.django_db
def test_mentor_training_approval(new_mentor, module, module2):
    assert not new_mentor.profile.approved
    assert not module.is_finished_by_mentor(new_mentor)
    assert not module2.is_finished_by_mentor(new_mentor)

    assert module.is_accessible_by_mentor(new_mentor)
    assert not module2.is_accessible_by_mentor(new_mentor)

    module.mark_mentor_as_done(new_mentor)
    assert not new_mentor.profile.approved
    assert module.is_finished_by_mentor(new_mentor)
    assert not module2.is_finished_by_mentor(new_mentor)
    assert module.is_accessible_by_mentor(new_mentor)
    assert module2.is_accessible_by_mentor(new_mentor)

    module2.mark_mentor_as_done(new_mentor)
    assert new_mentor.profile.approved
    assert module.is_finished_by_mentor(new_mentor)
    assert module2.is_finished_by_mentor(new_mentor)
    assert module.is_accessible_by_mentor(new_mentor)
    assert module2.is_accessible_by_mentor(new_mentor)
