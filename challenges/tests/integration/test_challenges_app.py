# test libs
import pytest
from pyquery import PyQuery as pq

# fixtures
from challenges.tests.fixtures import *
from profiles.tests import student, mentor # TODO: move to profiles.tests.fixtures

# factories
from challenges.factories import ChallengeFactory, ProgressFactory, ExampleFactory
from profiles.factories import StudentFactory, MentorFactory
from cmcomments.factories import CommentFactory
from images.factories import ImageFactory

# django modules
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils.timezone import now

# app modules
from challenges.models import Stage, Example
from challenges.views import challenges, unclaimed_progresses, claim_progress, preview_inspiration, start_building
from challenges.templatetags.activity_count import activity_count
from challenges.templatetags.user_has_started_challenge import user_has_started_challenge
from cmcomments.models import Comment

# mark all as integration tests for -m filtering
pytestmark = pytest.mark.integration


@pytest.mark.django_db
def test_theme_str(theme):
    assert theme.__str__() == "Theme: name=MyTheme"

@pytest.mark.django_db
def test_challenges_response_code(rf, challenge, student):
    request = rf.get('/challenges/')
    request.user = AnonymousUser()
    response = challenges(request)
    assert response.status_code == 200

@pytest.mark.django_db
def test_challenges_render_challenges(client, challenge, student):
    response = client.get('/challenges/', follow=True)
    assert response.status_code == 200
    assert response.context['challenges'][0] == challenge

@pytest.mark.django_db
def test_challenges_filters_by_name(client, challenge, challenge2, theme, student):
    challenge.themes.add(theme)
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
def test_preview_inpsiration(rf, challenge, student):
    request = rf.get('/challenges/1/')
    request.user = student
    response = preview_inspiration(request, challenge.id)
    assert response.status_code == 200

@pytest.mark.django_db
def test_start_building(rf, challenge, student):
    request = rf.post('/challenges/1/start_building')
    request.user = student
    response = start_building(request, challenge.id)
    assert Progress.objects.filter(challenge=challenge, student=student).count() == 1

@pytest.mark.django_db
def test_preview_inspiration_renders_inspiration_preview(client, challenge, loggedInStudent):
    url = reverse('challenges:preview_inspiration', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/preview/inspiration.html' in [tmpl.name for tmpl in response.templates]
    assert response.status_code == 200

@pytest.mark.django_db
def test_preview_plan_renders_plan_preview(client, challenge, loggedInStudent):
    url = reverse('challenges:preview_plan', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/preview/plan.html' in [tmpl.name for tmpl in response.templates]
    assert response.status_code == 200

@pytest.mark.django_db
def test_preview_build_renders_build_preview(client, challenge, loggedInStudent):
    url = reverse('challenges:preview_build', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/preview/build.html' in [tmpl.name for tmpl in response.templates]
    assert response.status_code == 200

@pytest.mark.django_db
def test_preview_reflect_renders_reflect_preview(client, challenge, loggedInStudent):
    url = reverse('challenges:preview_reflect', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/preview/reflect.html' in [tmpl.name for tmpl in response.templates]
    assert response.status_code == 200

@pytest.mark.django_db
def test_challenge_progress_with_no_progress_redirects_to_preview(client, loggedInStudent, challenge):
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('challenges:preview_inspiration', kwargs={
        'challenge_id':challenge.id
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_furthest_progress_plan_redirects_to_plan(client, student_comment, loggedInStudent):
    student_comment.stage = Stage.plan.value
    student_comment.user = loggedInStudent
    student_comment.save()
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username': loggedInStudent.username,
        'stage': Stage.plan.name
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_furthest_progress_build_redirects_to_build(client, student_comment, loggedInStudent):
    student_comment.stage = Stage.build.value
    student_comment.user = loggedInStudent
    student_comment.save()
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username': loggedInStudent.username,
        'stage': Stage.build.name
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_furthest_progress_test_redirects_to_test(client, student_comment, loggedInStudent):
    student_comment.stage = Stage.test.value
    student_comment.user = loggedInStudent
    student_comment.save()
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username': loggedInStudent.username,
        'stage': Stage.test.name
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_furthest_progress_reflect_redirects_to_reflect(client, student_comment, loggedInStudent):
    student_comment.stage = Stage.reflect.value
    student_comment.user = loggedInStudent
    student_comment.save()
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username': loggedInStudent.username,
        'stage': Stage.reflect.name
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_furthest_progress_reflect_approved_redirects_to_reflect(client, student_comment, loggedInStudent):
    student_comment.stage = Stage.reflect.value
    student_comment.user = loggedInStudent
    student_comment.save()
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.approved = now()
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url)
    assert response.status_code == 302
    assert reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username': loggedInStudent.username,
        'stage': Stage.reflect.name
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_bad_stage_404s(client, challenge, loggedInStudent):
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':challenge.id,
        'username':loggedInStudent.username
    })
    response = client.get(url + "notastage")
    assert response.status_code == 404

@pytest.mark.django_db
def test_challenge_progress_renders_stage_templates(client, student_comment, loggedInStudent):
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.approved = now()
    progress.save()

    for stage in Stage:
        if stage == Stage.test:
            continue
        url = reverse('challenges:challenge_progress', kwargs={
            'challenge_id':progress.challenge.id,
            'username':loggedInStudent.username,
            'stage': stage.name
        })
        response = client.get(url)
        assert 'challenges/progress/%s.html' % stage.name in [tmpl.name for tmpl in response.templates]
        assert response.status_code == 200

@pytest.mark.django_db
def test_challenge_progress_renders_all_comments_together(client, progress, loggedInStudent):
    Comment.objects.bulk_create([
        Comment(challenge_progress=progress, text="build comment", user=loggedInStudent, stage=Stage.build.value),
        Comment(challenge_progress=progress, text="test comment", user=loggedInStudent, stage=Stage.test.value),
        Comment(challenge_progress=progress, text="reflect comment", user=loggedInStudent, stage=Stage.reflect.value),
        Comment(challenge_progress=progress, text="plan comment", user=loggedInStudent, stage=Stage.plan.value)
    ])
    progress.student = loggedInStudent
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username,
        'stage': Stage.build.name
    })
    response = client.get(url)
    assert response.status_code == 200
    assert set(response.context['comments'].all()) == set(Comment.objects.filter(user=loggedInStudent))

    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username,
        'stage': Stage.plan.name
    })
    response = client.get(url)
    assert response.status_code == 200
    assert set(response.context['comments'].all()) == set(Comment.objects.filter(user=loggedInStudent))

@pytest.mark.django_db
def test_user_has_started_challenge(progress, challenge2):
    student = progress.student
    challenge = progress.challenge
    assert user_has_started_challenge(student, challenge)
    assert not user_has_started_challenge(student, challenge2)

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

@pytest.mark.django_db
def test_activity_count(student, mentor, progress):
    assert activity_count(progress) == 0
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor)
    assert activity_count(progress) == 2

@pytest.mark.django_db
def test_activity_count_by_user(student, mentor, progress):
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor)
    assert activity_count(progress, student) == 2
    assert activity_count(progress, mentor) == 1

@pytest.mark.django_db
def test_activity_count_by_stage(student, mentor, progress):
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=student, stage=Stage.plan.value)
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=student, stage=Stage.build.value)
    Comment.objects.create(challenge_progress=progress, text="Comment test", user=mentor, stage=Stage.build.value)
    assert activity_count(progress, None, Stage.plan.name) == 1
    assert activity_count(progress, None, Stage.build.name) == 2
    assert activity_count(progress, None, Stage.plan.name, Stage.build.name) == 3

@pytest.mark.django_db
def test_examples_view_for_student_without_progress(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert not response.context['progress']
    assert not response.context['user_example']

    d = pq(response.content)
    assert d('#student-not-started')
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_progress_without_example(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert not response.context['user_example']

    d = pq(response.content)
    assert not d('#student-not-started')
    assert d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_without_example(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student, completed=True)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert not response.context['user_example']

    d = pq(response.content)
    assert not d('#student-not-started')
    assert not d('#student-in-progress')
    assert d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_with_example_pending(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student, completed=True)
    example = ExampleFactory(challenge=challenge, progress=progress)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert response.context['user_example']
    assert example in response.context['examples']

    d = pq(response.content)
    assert not d('#student-not-started')
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_with_example_approved(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student, completed=True)
    example = ExampleFactory(challenge=challenge, progress=progress, approved=True)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert response.context['user_example']
    assert example in response.context['examples']

    d = pq(response.content)
    assert not d('#student-not-started')
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_with_example_rejected(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student, completed=True)
    example = ExampleFactory(challenge=challenge, progress=progress, approved=False)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert not response.context['user_example']
    assert example not in response.context['examples']

    d = pq(response.content)
    assert not d('#student-not-started')
    assert not d('#student-in-progress')
    assert d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_non_student(client):
    challenge = ChallengeFactory()
    mentor = MentorFactory(username="mentor", password="password")

    client.login(username=mentor.username, password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    d = pq(response.content)
    assert not d('#student-not-started')
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_anonymous_on_public_challenge(client):
    challenge = ChallengeFactory(public=True)

    response = client.get('/challenges/%d/examples/' % (challenge.id), follow=False)

    assert response.status_code == 200
    d = pq(response.content)
    assert not d('#student-not-started')
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_anonymous_on_private_challenge(client):
    challenge = ChallengeFactory(public=False)

    response = client.get('/challenges/%d/examples/' % (challenge.id), follow=False)

    assert response.status_code == 302
    assert 'login' in response.url

@pytest.mark.django_db
def test_examples_view_for_approved_example_visibile_by_others(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student)
    example = ExampleFactory(challenge=challenge, progress=progress, approved=True)

    viewer = StudentFactory(username="student2", password="password")

    client.login(username="student2", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert example in response.context['examples']

@pytest.mark.django_db
def test_examples_view_for_pending_example_not_visible_by_others(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student)
    example = ExampleFactory(challenge=challenge, progress=progress)

    viewer = StudentFactory(username="student2", password="password")

    client.login(username="student2", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert example not in response.context['examples']

@pytest.mark.django_db
def test_examples_view_for_rejected_example_not_visible_by_others(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student)
    example = ExampleFactory(challenge=challenge, progress=progress, approved=False)

    viewer = StudentFactory(username="student2", password="password")

    client.login(username="student2", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert example not in response.context['examples']

@pytest.mark.django_db
def test_examples_view_when_adding_new_example(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, student=student)
    image = ImageFactory()
    comment = CommentFactory(user=student, challenge_progress=progress, image=image)

    client.login(username="student", password="password")
    response = client.post('/challenges/%d/examples/' % (challenge.id), {
        "example": image.id
    }, follow=True)

    assert response.status_code == 200
    assert response.context['examples'][0].image.id == image.id

@pytest.mark.django_db
def test_examples_view_when_adding_new_example_no_progress_error(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    image = ImageFactory()

    client.login(username="student", password="password")
    response = client.post('/challenges/%d/examples/add/' % (challenge.id), {
        "example": image.id
    }, follow=True)

    assert response.status_code == 404

@pytest.mark.django_db
def test_examples_view_when_adding_new_example_wrong_challenge_error(client):
    student = StudentFactory(username="student", password="password")

    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, student=student)
    image = ImageFactory()
    comment = CommentFactory(user=student, challenge_progress=progress, image=image)

    challenge2 = ChallengeFactory()
    progress2 = ProgressFactory(challenge=challenge2, student=student)
    image2 = ImageFactory()
    comment2 = CommentFactory(user=student, challenge_progress=progress, image=image)

    client.login(username="student", password="password")
    response = client.post('/challenges/%d/examples/add/' % (challenge2.id), {
        "example": image.id
    }, follow=True)

    assert response.status_code == 404

@pytest.mark.django_db
def test_examples_view_when_adding_new_example_not_a_student_error(client):
    challenge = ChallengeFactory()
    user = MentorFactory(username="user", password="password")
    progress = ProgressFactory(challenge=challenge, mentor=user)
    image = ImageFactory()
    comment = CommentFactory(user=user, challenge_progress=progress, image=image)

    client.login(username="user", password="password")
    response = client.post('/challenges/%d/examples/add/' % (challenge.id), {
        "example": image.id
    }, follow=True)

    assert response.status_code == 404

@pytest.mark.django_db
def test_examples_view_when_adding_new_example_already_exists_error(client):
    challenge = ChallengeFactory()
    user = StudentFactory(username="user", password="password")
    progress = ProgressFactory(challenge=challenge, student=user)
    image = ImageFactory()
    comment = CommentFactory(user=user, challenge_progress=progress, image=image)
    example = ExampleFactory(challenge=challenge, progress=progress, image=image)
    image2 = ImageFactory()
    comment2 = CommentFactory(user=user, challenge_progress=progress, image=image2)

    client.login(username="user", password="password")
    response = client.post('/challenges/%d/examples/' % (challenge.id), {
        "example": image2.id
    }, follow=True)

    assert response.status_code == 409

@pytest.mark.django_db
def test_examples_delete_view_deletes_example(client):
    user = StudentFactory(username="user", password="password")
    progress = ProgressFactory(student=user)
    example = ExampleFactory(challenge=progress.challenge, progress=progress)

    client.login(username=user.username, password='password')
    response = client.post('/challenges/%d/examples/delete/' % (progress.challenge.id), {
        "example-id": example.id
    }, follow=True)

    assert response.status_code == 200
    assert example not in response.context['examples']
    assert Example.objects.get(pk=example.id).approved == False

@pytest.mark.django_db
def test_examples_delete_view_cannot_delete_other_users_example(client):
    user = StudentFactory(username="user", password="password")
    progress = ProgressFactory(student=user)
    example = ExampleFactory(challenge=progress.challenge, progress=progress)

    user2 = StudentFactory(username="user2", password="password")
    client.login(username=user2.username, password='password')

    response = client.post('/challenges/%d/examples/delete/' % (progress.challenge.id), {
        "example-id": example.id
    }, follow=True)

    assert response.status_code == 404
    assert Example.objects.get(pk=example.id).approved != False

@pytest.mark.django_db
def test_example_queryset_from_progress():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, student=user)
    approved = ExampleFactory(challenge=challenge, progress=progress, approved=True)
    pending = ExampleFactory(challenge=challenge, progress=progress, approved=None)
    rejected = ExampleFactory(challenge=challenge, progress=progress, approved=False)

    challenge2 = ChallengeFactory()
    progress2 = ProgressFactory(challenge=challenge2, student=user)
    approved2 = ExampleFactory(challenge=challenge2, progress=progress2, approved=True)

    assert approved in Example.objects.from_progress(progress=progress)
    assert pending in Example.objects.from_progress(progress=progress)
    assert rejected in Example.objects.from_progress(progress=progress)
    assert approved2 not in Example.objects.from_progress(progress=progress)

@pytest.mark.django_db
def test_example_queryset_status():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, student=user)
    approved = ExampleFactory(challenge=challenge, progress=progress, approved=True)
    pending = ExampleFactory(challenge=challenge, progress=progress, approved=None)
    rejected = ExampleFactory(challenge=challenge, progress=progress, approved=False)

    assert approved in Example.objects.status(approved=True)
    assert pending not in Example.objects.status(approved=True)
    assert rejected not in Example.objects.status(approved=True)

    assert approved not in Example.objects.status(pending=True)
    assert pending in Example.objects.status(pending=True)
    assert rejected not in Example.objects.status(pending=True)

    assert approved not in Example.objects.status(rejected=True)
    assert pending not in Example.objects.status(rejected=True)
    assert rejected in Example.objects.status(rejected=True)

    assert approved not in Example.objects.status(approved=False)
    assert pending not in Example.objects.status(pending=False)
    assert rejected not in Example.objects.status(rejected=False)

    assert approved in Example.objects.status(approved=True, pending=True, rejected=True)
    assert pending in Example.objects.status(approved=True, pending=True, rejected=True)
    assert rejected in Example.objects.status(approved=True, pending=True, rejected=True)

@pytest.mark.django_db
def test_example_queryset_for_gallery():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, student=user)
    approved = ExampleFactory(challenge=challenge, progress=progress, approved=True)
    pending = ExampleFactory(challenge=challenge, progress=progress, approved=None)
    rejected = ExampleFactory(challenge=challenge, progress=progress, approved=False)

    assert approved in Example.objects.for_gallery(challenge_id=challenge.id).all()
    assert pending not in Example.objects.for_gallery(challenge_id=challenge.id).all()
    assert rejected not in Example.objects.for_gallery(challenge_id=challenge.id).all()

    assert approved in Example.objects.for_gallery(challenge=challenge).all()
    assert pending not in Example.objects.for_gallery(challenge=challenge).all()
    assert rejected not in Example.objects.for_gallery(challenge=challenge).all()

    assert approved in Example.objects.for_gallery(challenge=challenge, progress=progress).all()
    assert pending in Example.objects.for_gallery(challenge=challenge, progress=progress).all()
    assert rejected not in Example.objects.for_gallery(challenge=challenge, progress=progress).all()

@pytest.mark.django_db
def test_example_queryset_reject():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, student=user)
    pending = ExampleFactory(challenge=challenge, progress=progress, approved=None)

    assert Example.objects.status(pending=True).reject() == 1
    assert Example.objects.get(pk=pending.id).approved == False

@pytest.mark.django_db
def test_example_queryset_reject_many():
    ExampleFactory.create_batch(5, approved=None)
    ExampleFactory.create_batch(5, approved=True)

    assert Example.objects.status(pending=True).reject() == 5

@pytest.mark.django_db
def test_example_queryset_approve():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, student=user)
    pending = ExampleFactory(challenge=challenge, progress=progress, approved=None)

    assert Example.objects.status(pending=True).approve() == 1
    assert Example.objects.get(pk=pending.id).approved == True

@pytest.mark.django_db
def test_example_queryset_approve_many():
    ExampleFactory.create_batch(5, approved=None)
    ExampleFactory.create_batch(5, approved=False)

    assert Example.objects.status(pending=True).approve() == 5
