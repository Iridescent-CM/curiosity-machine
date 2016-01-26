import pytest
import mock
from .models import Challenge, Progress, Theme, Favorite, Stage, Filter
from cmcomments.models import Comment
from .views import challenges, challenge_progress_approve, unclaimed_progresses, claim_progress, challenge_progress, preview_inspiration, start_building
from profiles.tests import student, mentor
from django.contrib.auth.models import User, AnonymousUser
from .templatetags.user_has_started_challenge import user_has_started_challenge
from .templatetags.activity_count import activity_count
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.utils.timezone import now

@pytest.fixture
def loggedInStudent(client):
    student = User.objects.create_user(username='loggedinstudent', email='loggedinstudent@example.com', password='password')
    student.profile.is_student = True
    student.profile.approved = True
    student.profile.save()
    client.login(username='loggedinstudent', password='password')
    return student

@pytest.fixture
def student_comment(student, progress):
    return Comment.objects.create(challenge_progress=progress, text="Comment test", user=student)

@pytest.fixture
def theme():
    return Theme.objects.create(name="MyTheme")

@pytest.fixture
def challenge():
    return Challenge.objects.create(
        name="Test Challenge",
        draft=False,
        reflect_subheader='test reflect_subheader',
        build_subheader='test build_subheader'
    )

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
def test_preview_reflect_redirects_with_reflect_message(client, challenge, loggedInStudent):
    url = reverse('challenges:preview_reflect', kwargs={
        'challenge_id': challenge.id
    })
    response = client.get(url, follow=True)
    messages = list(response.context['messages'])
    assert len(messages) == 1
    assert "your mentor will approve" in str(messages[0])

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
def test_challenge_progress_furthest_progress_reflect_unapproved_redirects_to_build(client, student_comment, loggedInStudent):
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
        'stage': Stage.build.name
    }) in response.url

@pytest.mark.django_db
def test_challenge_progress_furthest_progress_build_approved_redirects_to_reflect(client, student_comment, loggedInStudent):
    student_comment.stage = Stage.build.value
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
def test_challenge_progress_shows_reflect_unapproved_message(client, student_comment, loggedInStudent):
    progress = student_comment.challenge_progress
    progress.student = loggedInStudent
    progress.save()
    url = reverse('challenges:challenge_progress', kwargs={
        'challenge_id':progress.challenge.id,
        'username':loggedInStudent.username,
        'stage': Stage.reflect.name
    })
    response = client.get(url, follow=True)
    messages = list(response.context['messages'])
    assert len(messages) == 1
    assert "mentor needs to approve" in str(messages[0])

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
def test_mentor_can_approve(rf, progress):
    assert not progress.approved

    request = rf.post('/challenges/1/approve', {'approve': 'anyvalue'})
    request.user = progress.mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 302
    assert Progress.objects.get(id=progress.id).approved

    request = rf.post('/challenges/1/approve', {})
    request.user = progress.mentor
    request.session = 'session'
    request._messages = FallbackStorage(request)
    response = challenge_progress_approve(request, progress.challenge.id, progress.student.username)
    assert response.status_code == 302
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
