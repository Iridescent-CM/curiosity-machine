import pytest

from challenges.tests import progress, challenge
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from challenges.models import Example
from .models import Comment, Stage

@pytest.fixture
def student():
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.is_student = True
    student.profile.save()
    return student

@pytest.fixture
def mentor():
    mentor = User.objects.create_user(username='mentor', email='mentor@example.com', password='password')
    mentor.profile.is_mentor = True
    mentor.profile.approved = True
    mentor.profile.save()
    return mentor

@pytest.fixture
def mentor_comment(mentor, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor)

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

@pytest.fixture
def loggedInStudent(client, student):
    client.login(username=student.username, password='password')
    return student

@pytest.fixture
def loggedInMentor(client, mentor):
    client.login(username=mentor.username, password='password')
    return mentor

@pytest.mark.django_db
def test_unread_comment_count_for_mentors(mentor, student, mentor_comment):
    assert not mentor_comment.read
    assert mentor.profile.get_unread_comment_count() == 0
    assert student.profile.get_unread_comment_count() == 1

    mentor_comment.read = True
    mentor_comment.save()
    assert student.profile.get_unread_comment_count() == 0

@pytest.mark.django_db
def test_unread_comment_count_for_students(mentor, student, student_comment):
    assert not student_comment.read
    assert mentor.profile.get_unread_comment_count() == 1
    assert student.profile.get_unread_comment_count() == 0

    student_comment.read = True
    student_comment.save()
    assert mentor.profile.get_unread_comment_count() == 0

@pytest.mark.django_db
def test_regular_student_comment(client, loggedInStudent, mentor, student_comment):
    post_data = {'text': 'test comment'}
    assert Comment.objects.count() == 1
    response = client.post(
        reverse('challenges:comments:comments', kwargs={'challenge_id': student_comment.challenge_progress.challenge.id, 'username': loggedInStudent.username, 'stage': 'build'}),
        post_data
    )
    assert Comment.objects.count() == 2
    assert response.status_code == 302
    assert reverse('challenges:challenge_progress', kwargs={'challenge_id': student_comment.challenge_progress.challenge.id, 'username': loggedInStudent.username}) in response.url

@pytest.mark.django_db
def test_regular_mentor_comment(client, loggedInMentor, mentor, mentor_comment, student):
    progress = mentor_comment.challenge_progress
    progress.student = student
    progress.mentor = mentor
    progress.save()

    post_data = {'text': 'test comment'}
    assert Comment.objects.count() == 1
    response = client.post(
        reverse('challenges:comments:comments', kwargs={'challenge_id': progress.challenge.id, 'username': student.username, 'stage': 'build'}),
        post_data
    )
    assert response.status_code == 302
    assert Comment.objects.count() == 2

    assert reverse('challenges:challenge_progress', kwargs={'challenge_id': progress.challenge.id, 'username': student.username}) in response.url

@pytest.mark.django_db
def test_feature_as_example_post(client, loggedInMentor, student, student_comment):
    progress = student_comment.challenge_progress
    progress.student = student
    progress.mentor = loggedInMentor
    progress.save()
    post_data = {'text': 'test comment'}
    assert Example.objects.count() == 0
    response = client.post(
        reverse('challenges:comments:feature_as_example', kwargs={'challenge_id': progress.challenge.id, 'username': student.username, 'stage': 'build', 'comment_id': student_comment.id}),
        post_data
    )
    assert Example.objects.count() == 1

@pytest.mark.django_db
def test_feature_as_example_delete(client, loggedInMentor, student, student_comment):
    progress = student_comment.challenge_progress
    progress.student = student
    progress.mentor = loggedInMentor
    progress.save()
    post_data = {'text': 'test comment'}
    assert Example.objects.count() == 0
    response = client.post(
        reverse('challenges:comments:feature_as_example', kwargs={'challenge_id': progress.challenge.id, 'username': student.username, 'stage': 'build', 'comment_id': student_comment.id}),
        post_data
    )
    assert Example.objects.count() == 1
    response = client.delete(
        reverse('challenges:comments:feature_as_example', kwargs={'challenge_id': progress.challenge.id, 'username': student.username, 'stage': 'build', 'comment_id': student_comment.id}),
        post_data
    )
    assert Example.objects.count() == 0