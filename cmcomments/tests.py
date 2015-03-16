import pytest

from profiles.tests import student, mentor, loggedInMentor
from challenges.tests import progress, challenge, example, loggedInStudent
from django.core.urlresolvers import reverse
from challenges.models import Stage, Example

from .models import Comment

@pytest.fixture
def mentor_comment(mentor, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor)

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

@pytest.mark.django_db
def test_unread_comment_count_for_student(mentor, student, mentor_comment):
    assert not mentor_comment.read
    assert mentor.profile.get_unread_comment_count() == 0
    assert student.profile.get_unread_comment_count() == 1

    mentor_comment.read = True
    mentor_comment.save()
    assert student.profile.get_unread_comment_count() == 0

@pytest.mark.django_db
def test_unread_comment_count_for_mentors(mentor, student, student_comment):
    assert not student_comment.read
    assert mentor.profile.get_unread_comment_count() == 1
    assert student.profile.get_unread_comment_count() == 0

    student_comment.read = True
    student_comment.save()
    assert mentor.profile.get_unread_comment_count() == 0

@pytest.mark.django_db
def test_create_comment_as_student(client, progress, loggedInStudent):
    progress.student = loggedInStudent
    progress.save()
    assert Comment.objects.count() == 0
    response = client.post(reverse('challenges:comments:comments', kwargs={'challenge_id':progress.challenge.id, 'username': progress.student.username, 'stage':'test'}), {'text': 'some comment'})
    assert Comment.objects.count() == 1
    assert response.status_code == 302

@pytest.mark.django_db
def test_create_comment_as_mentor(client, progress, loggedInMentor):
    progress.mentor = loggedInMentor
    progress.save()
    assert Comment.objects.count() == 0
    response = client.post(reverse('challenges:comments:comments', kwargs={'challenge_id':progress.challenge.id, 'username': progress.student.username, 'stage':'test'}), {'text': 'some comment'})
    assert Comment.objects.count() == 1
    assert response.status_code == 302

@pytest.mark.django_db
def test_create_reflect_comment_as_student(client, progress, loggedInStudent):
    progress.student = loggedInStudent
    progress.stage = Stage.reflect.value
    progress.save()
    assert Comment.objects.count() == 0
    response = client.post(reverse('challenges:comments:comments', kwargs={'challenge_id':progress.challenge.id, 'username': progress.student.username, 'stage':'reflect'}), {'text': 'some comment'})
    assert Comment.objects.count() == 1
    assert response.status_code == 302

@pytest.mark.django_db
def test_feature_as_example(client, student_comment, loggedInMentor):
    progress = student_comment.challenge_progress
    progress.mentor = loggedInMentor
    progress.stage = Stage.reflect.value
    progress.save()
    assert Example.objects.count() == 0
    response = client.post(reverse('challenges:comments:feature_as_example', kwargs={'challenge_id':progress.challenge.id, 'username': progress.student.username, 'stage':'reflect', 'comment_id': student_comment.id}))
    assert Example.objects.count() == 1
    assert response.status_code == 204

@pytest.mark.django_db
def test_delete_feature_as_example(client, student_comment, loggedInMentor):
    progress = student_comment.challenge_progress
    progress.mentor = loggedInMentor
    progress.stage = Stage.reflect.value
    progress.save()
    response = client.post(reverse('challenges:comments:feature_as_example', kwargs={'challenge_id':progress.challenge.id, 'username': progress.student.username, 'stage':'reflect', 'comment_id': student_comment.id}))
    assert Example.objects.count() == 1
    response = client.delete(reverse('challenges:comments:feature_as_example', kwargs={'challenge_id':progress.challenge.id, 'username': progress.student.username, 'stage':'reflect', 'comment_id': student_comment.id}))
    assert Example.objects.count() == 0
    assert response.status_code == 204