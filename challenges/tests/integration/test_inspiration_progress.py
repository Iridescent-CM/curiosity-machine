import pytest

from django.core.urlresolvers import reverse

from challenges.factories import ChallengeFactory, ExampleFactory, ProgressFactory
from profiles.factories import StudentFactory, MentorFactory, EducatorFactory, ParentFactory, ParentConnectionFactory
from groups.factories import GroupFactory

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_inspiration_progress_view_as_student_renders_student_template(client):
    challenge = ChallengeFactory()
    user = StudentFactory(username='user', password='123123')
    progress = ProgressFactory(challenge=challenge, student=user)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, user.username), follow=True)

    assert response.status_code == 200
    assert "challenges/edp/progress/student/inspiration.html" == response.templates[0].name

@pytest.mark.django_db
def test_student_template_gets_progress(client):
    challenge = ChallengeFactory()
    user = StudentFactory(username='user', password='123123')
    progress = ProgressFactory(challenge=challenge, student=user)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, user.username), follow=True)

    assert response.status_code == 200
    assert response.context['progress'] == progress

@pytest.mark.django_db
def test_student_template_gets_examples(client):
    challenge = ChallengeFactory()
    examples = ExampleFactory.create_batch(2, challenge=challenge, approved=True)
    user = StudentFactory(username='user', password='123123')
    progress = ProgressFactory(challenge=challenge, student=user)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, user.username), follow=True)

    assert response.status_code == 200
    assert set(response.context['examples']) == set(examples)

@pytest.mark.django_db
def test_student_cannot_view_other_student_progress_inspirations(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    user = StudentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={
        "challenge_id": challenge.id
    }))

@pytest.mark.django_db
def test_renders_nonstudent_template_with_challenge_for_nonstudent_user(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    user = MentorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=True)

    assert response.status_code == 200
    assert response.context['challenge'] == challenge
    assert "challenges/edp/progress/inspiration_user.html" == response.templates[0].name

@pytest.mark.django_db
def test_nonstudent_template_gets_examples(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    examples = ExampleFactory.create_batch(2, challenge=challenge, approved=True)
    user = MentorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=True)

    assert response.status_code == 200
    assert set(response.context['examples']) == set(examples)

@pytest.mark.django_db
def test_anonymous_user_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)

    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=True)

    assert response.status_code == 200
    assert "registration/login.html" == response.templates[0].name

@pytest.mark.django_db
def test_connected_educator_access_granted(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    educator = EducatorFactory(username='user', password='123123')
    group = GroupFactory(owners=[educator], members=[progress.student])

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_unconnected_educator_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    educator = EducatorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={
        "challenge_id": challenge.id
    }))

@pytest.mark.django_db
def test_connected_parent_access_granted(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    parent = ParentFactory(username='user', password='123123')
    ParentConnectionFactory(parent_profile=parent.profile, child_profile=progress.student.profile, active=True)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 200

@pytest.mark.django_db
def test_unconnected_parent_access_denied(client):
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge)
    parent = ParentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/%s/inspiration/' % (challenge.id, progress.student.username), follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:preview_inspiration", kwargs={
        "challenge_id": challenge.id
    }))
