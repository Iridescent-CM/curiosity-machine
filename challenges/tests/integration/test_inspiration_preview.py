import pytest

from challenges.factories import *
from profiles.factories import StudentFactory, MentorFactory, EducatorFactory, ParentFactory

from django.core.urlresolvers import reverse

@pytest.mark.django_db
def test_renders_anonymous_template_with_challenge_for_anonymous_user(client):
    challenge = ChallengeFactory()
    response = client.get('/challenges/%d/' % challenge.id, follow=True)
    assert response.status_code == 200
    assert "challenges/edp/preview/inspiration_anonymous.html" == response.templates[0].name
    assert response.context['challenge'] == challenge

@pytest.mark.django_db
def test_context_includes_resources_and_col_width_helper(client):
    challenge = ChallengeFactory()
    challenge2 = ChallengeFactory()
    resource = ResourceFactory(challenge=challenge2)
    response = client.get('/challenges/%d/' % challenge.id, follow=True)
    assert not response.context['resources']
    assert response.context['col_width'] == 6
    response = client.get('/challenges/%d/' % challenge2.id, follow=True)
    assert set(response.context['resources']) == set([resource])
    assert response.context['col_width'] == 4

@pytest.mark.django_db
def test_renders_student_template_with_challenge_for_student_user_without_progress(client):
    challenge = ChallengeFactory()
    user = StudentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True)

    assert response.status_code == 200
    assert "challenges/edp/preview/student/inspiration.html" == response.templates[0].name
    assert response.context['challenge'] == challenge

@pytest.mark.django_db
def test_student_template_gets_examples(client):
    challenge = ChallengeFactory()
    examples = ExampleFactory.create_batch(2, challenge=challenge, approved=True)
    user = StudentFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True)

    assert response.status_code == 200
    assert set(response.context['examples']) == set(examples)

@pytest.mark.django_db
def test_redirects_student_with_progress_to_their_progress(client):
    challenge = ChallengeFactory()
    user = StudentFactory(username='user', password='123123')
    progress = ProgressFactory(challenge=challenge, student=user)

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=False)

    assert response.status_code == 302
    assert response.url.endswith(reverse("challenges:challenge_progress", kwargs={
        "challenge_id": challenge.id,
        "username": user.username
    }))

@pytest.mark.django_db
def test_renders_nonstudent_template_with_challenge_for_nonstudent_user(client):
    challenge = ChallengeFactory()
    user = MentorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True)

    assert response.status_code == 200
    assert "challenges/edp/preview/inspiration_user.html" == response.templates[0].name
    assert response.context['challenge'] == challenge

@pytest.mark.django_db
def test_nonstudent_template_gets_examples(client):
    challenge = ChallengeFactory()
    examples = ExampleFactory.create_batch(2, challenge=challenge, approved=True)
    user = MentorFactory(username='user', password='123123')

    client.login(username='user', password='123123')
    response = client.get('/challenges/%d/' % challenge.id, follow=True)

    assert response.status_code == 200
    assert set(response.context['examples']) == set(examples)

@pytest.mark.django_db
def test_challenge_decorated_with_user_accessibility_for_all_types(client):
    challenge = ChallengeFactory()

    for i, Factory in enumerate([StudentFactory, MentorFactory, EducatorFactory, ParentFactory]):
        user = StudentFactory(username="user%d" % i, password="password")

        client.login(username="user%d" % i, password="password")
        response = client.get("/challenges/%d/" % challenge.id, follow=True)

        assert response.status_code == 200
        assert hasattr(response.context["challenge"], "accessible")
