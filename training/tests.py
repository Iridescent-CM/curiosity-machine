import pytest
from .models import Module, Comment
from .views import module as module_view
from .views import comments, approve_module_progress
from profiles.tests import student, mentor
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied

NEW_MENTOR_USERNAME = "newbie"
NEW_MENTOR_EMAIL = "newbie@example.com"
ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "admin@example.com"

@pytest.fixture
def new_mentor(): # not approved
    mentor = User.objects.create(username=NEW_MENTOR_USERNAME, email=NEW_MENTOR_EMAIL)
    mentor.profile.is_mentor = True
    mentor.profile.save()
    return mentor

@pytest.fixture
def admin():
    admin = User.objects.create(username=ADMIN_USERNAME, email=ADMIN_EMAIL, is_staff=True, is_superuser=True)
    admin.profile.save()
    return admin

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
    with pytest.raises(PermissionDenied):
        response = module_view(request, module.id)

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
    with pytest.raises(PermissionDenied):
        response = comments(request, module.id)

@pytest.mark.django_db
def test_comments_top_level(rf, student, new_mentor, module):
    assert Comment.objects.count() == 0
    request = rf.post('/training/1/comments/', {'text': 'test_text'})
    request.user = new_mentor
    response = comments(request, module.id)
    assert response.status_code < 400
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
    assert response.status_code < 400
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

@pytest.mark.django_db
def test_approve_module_progress_view_status_code(rf, admin, mentor, new_mentor, module, module2):
    assert not new_mentor.profile.approved
    assert not module.is_finished_by_mentor(new_mentor)
    assert not module2.is_finished_by_mentor(new_mentor)

    # first, verify that a non-admin mentor can NOT hit this endpoint
    request = rf.post('/training/1/approve/{}/'.format(new_mentor.username))
    request.user = mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    with pytest.raises(PermissionDenied):
        response = approve_module_progress(request, module_id=module.id, username=new_mentor.username)
    assert not new_mentor.profile.approved
    assert not module.is_finished_by_mentor(new_mentor)
    assert not module2.is_finished_by_mentor(new_mentor)

    # now verify that a real admin can
    request = rf.post('/training/1/approve/{}/'.format(new_mentor.username))
    request.user = admin
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = approve_module_progress(request, module_id=module.id, username=new_mentor.username)
    assert response.status_code < 400
    assert not new_mentor.profile.approved
    assert module.is_finished_by_mentor(new_mentor)
    assert not module2.is_finished_by_mentor(new_mentor)

    request = rf.post('/training/2/approve/{}/'.format(new_mentor.username))
    request.user = admin
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = approve_module_progress(request, module_id=module2.id, username=new_mentor.username)
    assert response.status_code < 400
    assert User.objects.get(id=new_mentor.id).profile.approved
    assert module.is_finished_by_mentor(new_mentor)
    assert module2.is_finished_by_mentor(new_mentor)
