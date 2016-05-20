import pytest

from challenges.factories import ChallengeFactory, ExampleFactory, ProgressFactory
from profiles.factories import StudentFactory, MentorFactory

pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_nonpublic_challenges_require_login(client):
    challenge = ChallengeFactory( public=False )
    response = client.get('/challenges/%d/' % challenge.id, follow=True)
    assert response.status_code == 200
    assert "registration/login.html" == response.templates[0].name

@pytest.mark.django_db
def test_renders_anonymous_template_with_challenge_for_anonymous_user(client):
    challenge = ChallengeFactory( public=True )
    response = client.get('/challenges/%d/' % challenge.id, follow=True) 
    assert response.status_code == 200
    assert response.context['challenge'] == challenge
    assert "challenges/edp/preview/inspiration_anonymous.html" == response.templates[0].name

@pytest.mark.django_db
def test_renders_student_template_with_challenge_for_student_user(client):
    challenge = ChallengeFactory( public=True )
    user = StudentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True) 

    assert response.status_code == 200
    assert response.context['challenge'] == challenge
    assert "challenges/edp/preview/student/inspiration.html" == response.templates[0].name

@pytest.mark.django_db
def test_student_template_gets_examples(client):
    challenge = ChallengeFactory( public=True )
    examples = ExampleFactory.create_batch(2, challenge=challenge, approved=True)
    user = StudentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True) 

    assert response.status_code == 200
    assert set(response.context['examples']) == set(examples)

@pytest.mark.django_db
def test_student_template_gets_progress_if_it_exists(client):
    challenge = ChallengeFactory( public=True )
    user = StudentFactory(username='user', password='123123')
    progress = ProgressFactory(challenge=challenge, student=user)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True) 

    assert response.status_code == 200
    assert response.context['progress'] == progress

@pytest.mark.django_db
def test_renders_nonstudent_template_with_challenge_for_nonstudent_user(client):
    challenge = ChallengeFactory( public=True )
    user = MentorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True) 

    assert response.status_code == 200
    assert response.context['challenge'] == challenge
    assert "challenges/edp/preview/inspiration_user.html" == response.templates[0].name

@pytest.mark.django_db
def test_nonstudent_template_gets_examples(client):
    challenge = ChallengeFactory( public=True )
    examples = ExampleFactory.create_batch(2, challenge=challenge, approved=True)
    user = MentorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True) 

    assert response.status_code == 200
    assert set(response.context['examples']) == set(examples)
