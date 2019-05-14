#
# NOTE:
# This file should generally not be added to. Tests here should be split out to
# more specifically scoped test files over time.

# test libs
import pytest
from pyquery import PyQuery as pq

# fixtures
from challenges.tests.fixtures import *

# factories
from challenges.factories import *
from cmcomments.factories import *
from images.factories import *
from mentors.factories import *
from profiles.factories import *
from students.factories import *

# django modules
from django.contrib.auth.models import AnonymousUser
from django.core.urlresolvers import reverse
from django.core.exceptions import PermissionDenied
from django.contrib.messages.storage.fallback import FallbackStorage
from django.utils.timezone import now

# app modules
from challenges.models import Stage, Example
from challenges.views import challenges, claim_progress, start_building
from challenges.templatetags.activity_count import activity_count
from challenges.templatetags.user_has_started_challenge import user_has_started_challenge
from cmcomments.models import Comment

@pytest.fixture
def student():
    return StudentFactory()

@pytest.fixture
def mentor():
    return MentorFactory()

@pytest.mark.django_db
def test_theme_str(theme):
    assert theme.__str__() == "Theme: name=MyTheme"

@pytest.mark.django_db
def test_start_building(rf, challenge, student):
    challenge.free = True
    challenge.save()
    request = rf.post('/challenges/1/start_building')
    request.user = student
    response = start_building(request, challenge_id=challenge.id)
    assert Progress.objects.filter(challenge=challenge, owner=student).count() == 1

@pytest.mark.django_db
def test_preview_plan_renders_plan_preview(client, challenge, loggedInStaff):
    url = reverse('challenges:preview_plan', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/edp/preview/plan.html' in [tmpl.name for tmpl in response.templates]
    assert response.status_code == 200

@pytest.mark.django_db
def test_preview_build_renders_build_preview(client, challenge, loggedInStaff):
    url = reverse('challenges:preview_build', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/edp/preview/build.html' in [tmpl.name for tmpl in response.templates]
    assert response.status_code == 200

@pytest.mark.django_db
def test_preview_reflect_renders_reflect_preview(client, challenge, loggedInStaff):
    url = reverse('challenges:preview_reflect', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url)
    assert 'challenges/edp/preview/reflect.html' in [tmpl.name for tmpl in response.templates]
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
    progress.owner = loggedInStudent
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
    progress.owner = loggedInStudent
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
    progress.owner = loggedInStudent
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
    progress.owner = loggedInStudent
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
    progress.owner = loggedInStudent
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
    progress.owner = loggedInStudent
    progress.approved = now()
    progress.save()

    for stage in Stage:
        if stage in [Stage.test, Stage.inspiration]:
            continue
        url = reverse('challenges:challenge_progress', kwargs={
            'challenge_id':progress.challenge.id,
            'username':loggedInStudent.username,
            'stage': stage.name
        })
        response = client.get(url)
        assert 'challenges/edp/progress/%s.html' % stage.name in [tmpl.name for tmpl in response.templates]
        assert response.status_code == 200

@pytest.mark.django_db
def test_challenge_progress_renders_all_comments_together(client, progress, loggedInStudent):
    Comment.objects.bulk_create([
        Comment(challenge_progress=progress, text="build comment", user=loggedInStudent, stage=Stage.build.value),
        Comment(challenge_progress=progress, text="test comment", user=loggedInStudent, stage=Stage.test.value),
        Comment(challenge_progress=progress, text="reflect comment", user=loggedInStudent, stage=Stage.reflect.value),
        Comment(challenge_progress=progress, text="plan comment", user=loggedInStudent, stage=Stage.plan.value)
    ])
    progress.owner = loggedInStudent
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
    student = progress.owner
    challenge = progress.challenge
    assert user_has_started_challenge(student, challenge)
    assert not user_has_started_challenge(student, challenge2)

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
    request.user = unclaimed_progress.owner
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
    Comment.objects.create(challenge_progress=unclaimed_progress, text="Comment test", user=unclaimed_progress.owner)
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
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_progress_without_example(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert not response.context['user_example']

    d = pq(response.content)
    assert d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_without_example(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student, completed=True)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert not response.context['user_example']

    d = pq(response.content)
    assert not d('#student-in-progress')
    assert d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_with_example_pending(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student, completed=True)
    example = ExampleFactory(progress=progress)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert response.context['user_example']
    assert example in response.context['examples']

    d = pq(response.content)
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_with_example_approved(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student, completed=True)
    example = ExampleFactory(progress=progress, approved=True)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert response.context['user_example']
    assert example in response.context['examples']

    d = pq(response.content)
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_student_with_completed_progress_with_example_rejected(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student, completed=True)
    example = ExampleFactory(progress=progress, approved=False)

    client.login(username="student", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert response.context['challenge']
    assert response.context['progress']
    assert not response.context['user_example']
    assert example not in response.context['examples']

    d = pq(response.content)
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
    assert not d('#student-in-progress')
    assert not d('#student-completed')
    assert not d('#student-example-pending')

@pytest.mark.django_db
def test_examples_view_for_anonymous(client):
    challenge = ChallengeFactory()

    response = client.get('/challenges/%d/examples/' % (challenge.id), follow=False)

    assert response.status_code == 302
    assert 'login' in response.url

@pytest.mark.django_db
def test_examples_view_for_approved_example_visibile_by_others(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student)
    example = ExampleFactory(progress=progress, approved=True)

    viewer = StudentFactory(username="student2", password="password")

    client.login(username="student2", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert example in response.context['examples']

@pytest.mark.django_db
def test_examples_view_for_pending_example_not_visible_by_others(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student)
    example = ExampleFactory(progress=progress)

    viewer = StudentFactory(username="student2", password="password")

    client.login(username="student2", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert example not in response.context['examples']

@pytest.mark.django_db
def test_examples_view_for_rejected_example_not_visible_by_others(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student)
    example = ExampleFactory(progress=progress, approved=False)

    viewer = StudentFactory(username="student2", password="password")

    client.login(username="student2", password="password")
    response = client.get('/challenges/%d/examples' % (challenge.id), follow=True)

    assert example not in response.context['examples']

@pytest.mark.django_db
def test_examples_view_when_adding_new_example(client):
    challenge = ChallengeFactory()
    student = StudentFactory(username="student", password="password")
    progress = ProgressFactory(challenge=challenge, owner=student)
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
    progress = ProgressFactory(challenge=challenge, owner=student)
    image = ImageFactory()
    comment = CommentFactory(user=student, challenge_progress=progress, image=image)

    challenge2 = ChallengeFactory()
    progress2 = ProgressFactory(challenge=challenge2, owner=student)
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
    progress = ProgressFactory(challenge=challenge, owner=user)
    image = ImageFactory()
    comment = CommentFactory(user=user, challenge_progress=progress, image=image)
    example = ExampleFactory(progress=progress, image=image)
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
    progress = ProgressFactory(owner=user)
    example = ExampleFactory(progress=progress)

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
    progress = ProgressFactory(owner=user)
    example = ExampleFactory(progress=progress)

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
    progress = ProgressFactory(challenge=challenge, owner=user)
    approved = ExampleFactory(progress=progress, approved=True)
    pending = ExampleFactory(progress=progress, approved=None)
    rejected = ExampleFactory(progress=progress, approved=False)

    challenge2 = ChallengeFactory()
    progress2 = ProgressFactory(challenge=challenge2, owner=user)
    approved2 = ExampleFactory(progress=progress2, approved=True)

    assert approved in Example.objects.from_progress(progress=progress)
    assert pending in Example.objects.from_progress(progress=progress)
    assert rejected in Example.objects.from_progress(progress=progress)
    assert approved2 not in Example.objects.from_progress(progress=progress)

@pytest.mark.django_db
def test_example_queryset_status():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, owner=user)
    approved = ExampleFactory(progress=progress, approved=True)
    pending = ExampleFactory(progress=progress, approved=None)
    rejected = ExampleFactory(progress=progress, approved=False)

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
    progress = ProgressFactory(challenge=challenge, owner=user)
    approved = ExampleFactory(progress=progress, approved=True)
    pending = ExampleFactory(progress=progress, approved=None)
    rejected = ExampleFactory(progress=progress, approved=False)

    assert approved in Example.objects.for_gallery(challenge_id=challenge.id).all()
    assert pending not in Example.objects.for_gallery(challenge_id=challenge.id).all()
    assert rejected not in Example.objects.for_gallery(challenge_id=challenge.id).all()

    assert approved in Example.objects.for_gallery(challenge=challenge).all()
    assert pending not in Example.objects.for_gallery(challenge=challenge).all()
    assert rejected not in Example.objects.for_gallery(challenge=challenge).all()

    assert approved in Example.objects.for_gallery(challenge=challenge, user=user).all()
    assert pending in Example.objects.for_gallery(challenge=challenge, user=user).all()
    assert rejected not in Example.objects.for_gallery(challenge=challenge, user=user).all()

@pytest.mark.django_db
def test_example_queryset_for_gallery_preview_returns_subset():
    challenge = ChallengeFactory()
    examples = ExampleFactory.create_batch(5, progress__challenge=challenge, approved=True)

    assert Example.objects.for_gallery_preview(challenge=challenge).count() == 4
    assert set(Example.objects.for_gallery_preview(challenge=challenge)).issubset(set(examples))

@pytest.mark.django_db
def test_example_queryset_reject():
    user = StudentFactory(username="user", password="password")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, owner=user)
    pending = ExampleFactory(progress=progress, approved=None)

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
    progress = ProgressFactory(challenge=challenge, owner=user)
    pending = ExampleFactory(progress=progress, approved=None)

    assert Example.objects.status(pending=True).approve() == 1
    assert Example.objects.get(pk=pending.id).approved == True

@pytest.mark.django_db
def test_example_queryset_approve_many():
    ExampleFactory.create_batch(5, approved=None)
    ExampleFactory.create_batch(5, approved=False)

    assert Example.objects.status(pending=True).approve() == 5
