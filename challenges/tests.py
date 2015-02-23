import pytest
from .models import Challenge, Progress, Theme, Favorite, Stage, Filter
from cmcomments.models import Comment
from .views import challenges, challenge_progress_approve, unclaimed_progresses, claim_progress
from .views import challenge as challenge_view # avoid conflict with appropriately-named fixture
from profiles.tests import student, mentor
from django.contrib.auth.models import User, AnonymousUser
from .templatetags.user_has_started_challenge import user_has_started_challenge
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied

@pytest.fixture
def loggedInStudent(client):
    student = User.objects.create_user(username='student', email='student@example.com', password='password')
    student.profile.approved = True
    student.profile.save()
    client.login(username='student', password='password')
    return student

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

@pytest.fixture
def theme():
    return Theme.objects.create(name="MyTheme")

@pytest.fixture
def challenge():
    return Challenge.objects.create(name="Test Challenge", draft=False)

@pytest.fixture
def filter():
    return Filter.objects.create(name="My Filter")

@pytest.fixture
def challenge2():
    return Challenge.objects.create(name="Test Challenge 2", draft=False)

@pytest.fixture
def progress(student, mentor, challenge):
    return Progress.objects.create(student=student, mentor=mentor, challenge=challenge)

@pytest.fixture
def unclaimed_progress(student, challenge):
    return Progress.objects.create(student=student, challenge=challenge)

@pytest.mark.django_db
def test_theme_str(theme):
    assert theme.__str__() == "Theme: name=MyTheme"

@pytest.mark.django_db
def test_challenges_response_code(rf, challenge, student):
    request = rf.get('/challenges/')
    response = challenges(request)
    assert response.status_code == 200

@pytest.mark.django_db
def test_challenges_render_challenges(client, challenge, student):
    response = client.get('/challenges/', follow=True)
    assert response.status_code == 200
    assert response.context['challenges'][0] == challenge

@pytest.mark.django_db
def test_challenges_filters_by_name(client, challenge, challenge2, theme, student):
    challenge.theme = theme
    challenge.save()

    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    response = client.get('/challenges/', {'theme': theme.name}, follow=True)
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_challenges_filters_drafts(client, challenge, challenge2, student):
    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    challenge.draft = True
    challenge.save()

    response = client.get('/challenges/')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_ajax_challenges(client, loggedInStudent, challenge):
    response = client.get('/challenges/ajax_challenges', follow=True)
    assert response.status_code == 200
    assert response.context['challenges'][0] == challenge

@pytest.mark.django_db
def test_ajax_challenges_filters_by_name(client, loggedInStudent, challenge, challenge2, theme):
    challenge.theme = theme
    challenge.save()

    response = client.get('/challenges/ajax_challenges')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    response = client.get('/challenges/ajax_challenges', {'theme': theme.name}, follow=True)
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_ajax_challenges_filters_drafts(client, loggedInStudent, challenge, challenge2):
    response = client.get('/challenges/ajax_challenges')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 2

    challenge.draft = True
    challenge.save()

    response = client.get('/challenges/ajax_challenges')
    assert response.status_code == 200
    assert len(response.context['challenges']) == 1

@pytest.mark.django_db
def test_challenge_response_code(rf, challenge, student):
    request = rf.get('/challenges/1/')
    request.user = AnonymousUser()
    response = challenge_view(request, challenge.id)
    assert response.status_code == 200

    request = rf.get('/challenges/1/')
    request.user = student
    response = challenge_view(request, challenge.id)
    assert response.status_code == 200

@pytest.mark.django_db
def test_user_has_started_challenge(progress, challenge2):
    student = progress.student
    challenge = progress.challenge
    assert user_has_started_challenge(student, challenge)
    assert not user_has_started_challenge(student, challenge2)

@pytest.mark.django_db
def test_mentor_can_approve(rf, progress):
    assert not progress.approved

    request = rf.post('/challenges/1/approve')
    request.user = progress.mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 204
    assert Progress.objects.get(id=progress.id).approved

    request = rf.delete('/challenges/1/approve')
    request.user = progress.mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 204
    assert not Progress.objects.get(id=progress.id).approved

@pytest.mark.django_db
def test_student_cannot_approve(rf, progress):
    assert not progress.approved

    request = rf.post('/challenges/1/approve')
    request.user = progress.student
    with pytest.raises(PermissionDenied):
        response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert not Progress.objects.get(id=progress.id).approved

@pytest.mark.django_db
def test_unclaimed_progresses_response_code(rf, mentor, unclaimed_progress):
    request = rf.get('/challenges/unclaimed/')
    request.user = mentor
    response = unclaimed_progresses(request)
    assert response.status_code == 200

    request = rf.get('/challenges/unclaimed/')
    request.user = unclaimed_progress.student
    with pytest.raises(PermissionDenied):
        response = unclaimed_progresses(request)

@pytest.mark.django_db
def test_claim_progress(rf, mentor, unclaimed_progress):
    assert not unclaimed_progress.mentor

    request = rf.post('/challenges/unclaimed/1')
    request.user = mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = claim_progress(request, unclaimed_progress.id)
    assert response.status_code == 302
    assert Progress.objects.get(id=unclaimed_progress.id).mentor == mentor

@pytest.mark.django_db
def test_student_cannot_claim_progress(rf, unclaimed_progress):
    assert not unclaimed_progress.mentor

    request = rf.post('/challenges/unclaimed/1')
    request.user = unclaimed_progress.student
    with pytest.raises(PermissionDenied):
        response = claim_progress(request, unclaimed_progress.id)
    assert not Progress.objects.get(id=unclaimed_progress.id).mentor

@pytest.mark.django_db
def test_is_favorited(challenge, student):
    assert challenge.is_favorite(student) == False
    Favorite.objects.create(challenge=challenge, student=student)
    assert challenge.is_favorite(student) == True

@pytest.mark.django_db
def test_unclaimed_progress(mentor, unclaimed_progress):
    assert not unclaimed_progress.mentor
    unclaimed = Progress.unclaimed()
    assert sum(1 for s in unclaimed) == 0
    unclaimed_progress.stage = Stage.plan
    unclaimed_progress.save()
    student_comment(unclaimed_progress.student, unclaimed_progress)
    unclaimed = Progress.unclaimed()
    assert sum(1 for s in unclaimed) == 1

@pytest.mark.django_db
def test_classify_with_id(filter, challenge):
    challenge.filters.add(filter)
    assert(challenge.filters.exists() == 1)

