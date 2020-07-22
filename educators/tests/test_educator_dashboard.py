import json
import mock
import pytest
from challenges.factories import *
from cmcomments.factories import *
from curiositymachine import signals
from datetime import timedelta
from django.contrib.auth import authenticate
from django.urls import reverse
from django.urls import reverse
from django.utils.timezone import now
from families.factories import *
from memberships.factories import *
from profiles.factories import *
from students.factories import *
from units.factories import *
from ..factories import *
from ..models import *

@pytest.mark.django_db
def test_challenges_page_context_has_membership_challenges(client):
    challenges = ChallengeFactory.create_batch(3, draft=False)
    educator = EducatorFactory(username="edu", password="123123")
    membership = MembershipFactory(members=[educator], challenges=challenges)

    client.login(username="edu", password="123123")
    response = client.get(reverse("educators:challenges"), follow=True)
    assert set(response.context["membership_challenges"]) == set(challenges)
    assert response.context["membership"] == membership

@pytest.mark.django_db
def test_student_detail_page_context_has_connected_student(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    challenges = ChallengeFactory.create_batch(3, draft=False)
    membership = MembershipFactory(members=[educator, student])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert response.context["student"] == student

@pytest.mark.django_db
def test_student_detail_page_403s_on_non_membership_educator(client):
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": 1}),
        follow=True
    )
    assert response.status_code == 403

@pytest.mark.django_db
def test_student_detail_page_404s_on_non_connected_student(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    membership = MembershipFactory(members=[educator])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_student_detail_page_404s_on_non_student_membership_member(client):
    educator = EducatorFactory(username="edu", password="123123")
    educator2 = EducatorFactory(username="educator2", password="123123")
    family = FamilyFactory()
    membership = MembershipFactory(members=[educator, educator2, family])

    client.login(username="edu", password="123123")

    response = client.get(
        reverse("educators:student", kwargs={"student_id": educator2.id}),
        follow=True
    )
    assert response.status_code == 404

    response = client.get(
        reverse("educators:student", kwargs={"student_id": family.id}),
        follow=True
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_student_detail_page_context_has_graph_data_url(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    progress = ProgressFactory(owner=student, comment=True)
    membership = MembershipFactory(members=[educator, student], challenges=[progress.challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert response.context["graph_data_url"] == reverse("educators:progress_graph_data") + "?id=%d" % progress.id

@pytest.mark.django_db
def test_student_detail_page_context_has_membership_progresses(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    progresses = ProgressFactory.create_batch(5, owner=student, comment=True)
    membership = MembershipFactory(members=[educator, student], challenges=[p.challenge for p in progresses])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert set(response.context["progresses"]) == set(progresses)

@pytest.mark.django_db
def test_student_detail_page_context_does_not_have_other_progresses(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    progresses = ProgressFactory.create_batch(5, owner=student, comment=True)
    membership = MembershipFactory(members=[educator, student], challenges=[p.challenge for p in progresses[:2]])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert set(response.context["progresses"]) == set(progresses[:2])

@pytest.mark.django_db
def test_student_detail_page_context_has_progress_annotations(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student", password="123123")
    progress = ProgressFactory(owner=student)
    membership = MembershipFactory(members=[educator, student], challenges=[progress.challenge])

    latest = CommentFactory(challenge_progress=progress, user=student, created=now(), stage=4)
    yesterday = now() - timedelta(days=1)
    CommentFactory(challenge_progress=progress, user=student, created=yesterday, stage=1)
    CommentFactory(challenge_progress=progress, user=student, created=yesterday, stage=1)
    CommentFactory(challenge_progress=progress, user=student, created=yesterday, stage=1)
    CommentFactory(challenge_progress=progress, user=student, created=yesterday, stage=2)

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert response.context["progresses"][0].total_user_comments == 5
    assert response.context["progresses"][0].latest_user_comment == latest
    assert response.context["progresses"][0].user_comment_counts_by_stage == [3, 1, 0, 1]

@pytest.mark.django_db
def test_student_detail_page_context_has_completed_count(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student")

    p1 = ProgressFactory(owner=student)
    p2 = ProgressFactory(owner=student, completed=True)

    membership = MembershipFactory(members=[educator, student], challenges=[p1.challenge, p2.challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert response.context["completed_count"] == 1

@pytest.mark.django_db
def test_student_detail_page_context_has_approved_example_count(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student")
    student2 = StudentFactory(username="student2")

    progress = ProgressFactory(owner=student, completed=True)
    approved = ExampleFactory(progress=progress, approved=True)
    ExampleFactory(progress=progress, approved=False)
    ExampleFactory(progress=progress)
    progress2 = ProgressFactory(owner=student2, completed=True)

    membership = MembershipFactory(members=[educator, student, student2], challenges=[progress.challenge, progress2.challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert response.context["progresses"][0].approved_examples == [approved]
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student2.id}),
        follow=True
    )
    assert response.context["progresses"][0].approved_examples == []

@pytest.mark.django_db
def test_student_detail_page_context_progresses_sort_by_activity(client):
    educator = EducatorFactory(username="edu", password="123123")
    student = StudentFactory(username="student")

    challengeA = ChallengeFactory(name="Challenge A", draft=False)
    challengeB = ChallengeFactory(name="Challenge B", draft=False)
    progressA = ProgressFactory(owner=student, challenge=challengeA)
    progressB = ProgressFactory(owner=student, challenge=challengeB)

    membership = MembershipFactory(members=[educator, student], challenges=[challengeA, challengeB])

    rightnow = now()
    client.login(username="edu", password="123123")

    CommentFactory(challenge_progress=progressA, user=student, created=rightnow - timedelta(minutes=3))
    CommentFactory(challenge_progress=progressB, user=student, created=rightnow - timedelta(minutes=4))
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert [p.id for p in response.context["progresses"]] == [p.id for p in [progressA, progressB]]

    CommentFactory(challenge_progress=progressA, user=student, created=rightnow - timedelta(minutes=2))
    CommentFactory(challenge_progress=progressB, user=student, created=rightnow - timedelta(minutes=1))
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert [p.id for p in response.context["progresses"]] == [p.id for p in [progressB, progressA]]

    CommentFactory(challenge_progress=progressA, user=student, created=rightnow)
    CommentFactory(challenge_progress=progressB, user=student, created=rightnow)
    response = client.get(
        reverse("educators:student", kwargs={"student_id": student.id}),
        follow=True
    )
    assert [p.id for p in response.context["progresses"]] == [p.id for p in [progressA, progressB]]

@pytest.mark.django_db
def test_students_page_403s_on_non_membership_educator(client):
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get(reverse("educators:students"), follow=True)
    assert response.status_code == 403

@pytest.mark.django_db
def test_participants_page_context_has_membership_participants(client):
    educator = EducatorFactory(username="edu", password="123123")
    other_educators = EducatorFactory.create_batch(4)
    students = StudentFactory.create_batch(10)
    families = FamilyFactory.create_batch(8)
    membership = MembershipFactory(members=[educator] + other_educators + students + families)

    client.login(username="edu", password="123123")
    response = client.get(reverse("educators:students"), follow=True)
    assert response.context["membership"] == membership
    assert set(response.context["participants"]) == set(students + families + [educator] + other_educators)

@pytest.mark.django_db
def test_challenge_detail_page_403s_on_non_membership_educator(client):
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    assert client.get(
        reverse("educators:challenge", kwargs={"challenge_id": 1}),
        follow=True
    ).status_code == 403

@pytest.mark.django_db
def test_challenge_detail_page_404s_on_non_membership_challenge(client):
    educator = EducatorFactory(username="edu", password="123123")
    challenge1 = ChallengeFactory()
    challenge2 = ChallengeFactory()
    membership = MembershipFactory(members=[educator], challenges=[challenge1])

    client.login(username="edu", password="123123")
    assert client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge1.id}),
        follow=True
    ).status_code == 200
    assert client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge2.id}),
        follow=True
    ).status_code == 404

@pytest.mark.django_db
def test_challenge_detail_page_context_has_challenge(client):
    educator = EducatorFactory(username="edu", password="123123")
    challenge = ChallengeFactory()
    membership = MembershipFactory(members=[educator], challenges=[challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge.id}),
        follow=True
    )
    assert response.context["challenge"] == challenge

@pytest.mark.django_db
def test_challenge_detail_page_context_has_totals_per_student(client):
    educator = EducatorFactory(username="edu", password="123123")
    challenge = ChallengeFactory()
    progress = ProgressFactory(challenge=challenge, comment=5)
    membership = MembershipFactory(members=[progress.owner, educator], challenges=[challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge.id}),
        follow=True
    )
    assert response.context["students"][0].user_comment_counts_by_stage

@pytest.mark.django_db
def test_challenge_details_page_shows_unstarted_students(client):
    educator = EducatorFactory(username="edu", password="123123")
    challenge = ChallengeFactory()
    student = StudentFactory()
    membership = MembershipFactory(members=[student, educator], challenges=[challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge.id}),
        follow=True
    )
    assert response.context["students"][0].user_comment_counts_by_stage == [0, 0, 0, 0]

@pytest.mark.django_db
def test_challenge_details_page_orders_students(client):
    educator = EducatorFactory(username="edu", password="123123")
    challenge = ChallengeFactory()
    students = [
        StudentFactory(first_name='', username='b_user'),
        StudentFactory(first_name='', username='a_user'),
        StudentFactory(first_name='b'),
        StudentFactory(first_name='a'),
    ]
    membership = MembershipFactory(members=students + [educator], challenges=[challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge.id}),
        follow=True
    )
    assert [s.id for s in response.context["students"]]== [s.id for s in reversed(students)]

@pytest.mark.django_db
def test_challenge_detail_page_context_has_gallery_post_indicator_for_approved_example(client):
    educator = EducatorFactory(username="edu", password="123123")
    student1 = StudentFactory()
    challenge = ChallengeFactory()
    progress1 = ProgressFactory(owner=student1, challenge=challenge)
    ExampleFactory(progress=progress1, approved=True)

    membership = MembershipFactory(members=[student1, educator], challenges=[challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse('educators:challenge', kwargs={"challenge_id": challenge.id}),
        follow=True
    )
    assert set(response.context["student_ids_with_examples"]) == set([student1.id])

@pytest.mark.django_db
def test_challenge_detail_page_context_does_not_have_gallery_post_indicator_otherwise(client):
    educator = EducatorFactory(username="edu", password="123123")
    student1 = StudentFactory()
    student2 = StudentFactory()
    student3 = StudentFactory()
    challenge = ChallengeFactory()
    progress1 = ProgressFactory(owner=student1, challenge=challenge)
    progress2 = ProgressFactory(owner=student2, challenge=challenge)
    progress3 = ProgressFactory(owner=student3, challenge=challenge)
    ExampleFactory(progress=progress1, approved=False)
    ExampleFactory(progress=progress2)

    membership = MembershipFactory(members=[student1, student2, student3, educator], challenges=[challenge])

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenge.id}),
        follow=True
    )
    assert len(response.context["student_ids_with_examples"]) == 0

@pytest.mark.django_db
def test_challenge_detail_page_context_has_challenge_links(client):
    educator = EducatorFactory(username="edu", password="123123")
    challenges = ChallengeFactory.create_batch(5)
    membership = MembershipFactory(members=[educator], challenges=challenges)

    client.login(username="edu", password="123123")
    response = client.get(
        reverse("educators:challenge", kwargs={"challenge_id": challenges[0].id}),
        follow=True
    )
    assert set(response.context["challenge_links"]) == set(challenges)

@pytest.mark.django_db
def test_page_contexts_have_membership_selection_helper(client):
    educator = EducatorFactory(username="edu", password="123123")
    memberships = [MembershipFactory(members=[educator]), MembershipFactory(members=[educator])]

    client.login(username="edu", password="123123")
    for url in [
        reverse("educators:challenges"),
        reverse("educators:students")
    ]:
        response = client.get(url, follow=True)
        assert "membership_selection" in response.context

@pytest.mark.django_db
def test_graph_data_endpoint_returns_json(client):
    educator = EducatorFactory(username="edu", password="123123")

    client.login(username="edu", password="123123")
    response = client.get(reverse("educators:progress_graph_data"))
    assert response['Content-Type'] == "application/json"

@pytest.mark.django_db
def test_graph_data_endpoint_requires_authentication_as_educator(client):
    user = UserFactory(username="user", password="123123")
    progress = ProgressFactory(comment=True)

    assert client.get(reverse("educators:progress_graph_data")).status_code == 403
    client.login(username="user", password="123123")
    assert client.get(reverse("educators:progress_graph_data")).status_code == 403

@pytest.mark.django_db
def test_graph_data_endpoint_returns_requested_data(client):
    educator = EducatorFactory(username="edu", password="123123")
    progress = ProgressFactory(comment=True)
    progress2 = ProgressFactory(comment=True)
    membership = MembershipFactory(members=[educator, progress.owner, progress2.owner])

    client.login(username="edu", password="123123")

    response = client.get(reverse("educators:progress_graph_data"))
    assert json.loads(response.content.decode('utf-8')) == []

    response = client.get(reverse("educators:progress_graph_data"), {'id': progress.id})
    data = json.loads(response.content.decode('utf-8'))
    assert len(data) == 1
    assert data[0]["challenge_progress_id"] == progress.id
    assert data[0]["user_id"] == progress.owner.id

    response = client.get(reverse("educators:progress_graph_data"), {'id': [progress.id, progress2.id]})
    data = json.loads(response.content.decode('utf-8'))
    assert len(data) == 2

@pytest.mark.django_db
def test_graph_data_endpoint_omits_data_without_membership_connection(client):
    educator = EducatorFactory(username="edu", password="123123")
    progress = ProgressFactory(comment=True)
    progress2 = ProgressFactory(comment=True)

    client.login(username="edu", password="123123")
    response = client.get(reverse("educators:progress_graph_data"), {'id': [progress.id, progress2.id]})
    assert json.loads(response.content.decode('utf-8')) == []

@pytest.mark.django_db
def test_educator_changes_student_password(client):
    educator = EducatorFactory(username='ed', password='123123')
    student = StudentFactory(username='student', password='123123')
    membership = MembershipFactory(members=[educator, student])

    assert authenticate(username='student', password='123123')
    assert authenticate(username='ed', password='123123')

    client.login(username='ed', password='123123')
    response = client.post(
        reverse("educators:student_password_reset", kwargs={"student_id": student.id}),
        {
            "password1": '987987',
            "password2": '987987',
        }
    )

    assert response.status_code == 302
    assert response.url.endswith('/home/students/')
    assert authenticate(username='student', password='987987')
    assert authenticate(username='ed', password='123123')

@pytest.mark.django_db
def test_educator_changes_family_password(client):
    educator = EducatorFactory(username='ed', password='123123')
    family = FamilyFactory(username='family', password='123123')
    membership = MembershipFactory(members=[educator, family])

    assert authenticate(username='family', password='123123')
    assert authenticate(username='ed', password='123123')

    client.login(username='ed', password='123123')
    response = client.post(
        reverse("educators:student_password_reset", kwargs={"student_id": family.id}),
        {
            "password1": '987987',
            "password2": '987987',
        }
    )

    assert response.status_code == 302
    assert response.url.endswith('/home/students/')
    assert authenticate(username='family', password='987987')
    assert authenticate(username='ed', password='123123')

@pytest.mark.django_db
def test_educator_change_student_password_404s_for_bad_targets(client):
    educator = EducatorFactory(username='ed', password='123123')
    educator2 = EducatorFactory(username='ed2', password='123123')
    student = StudentFactory(username='student', password='123123')
    family = FamilyFactory()
    membership = MembershipFactory(members=[educator, educator2, student, family])
    student2 = StudentFactory(username='student2', password='123123')

    client.login(username='ed', password='123123')

    response = client.post(
        reverse("educators:student_password_reset", kwargs={"student_id": student2.id}),
        {
            "password1": '987987',
            "password2": '987987',
        }
    )
    assert response.status_code == 404
    response = client.post(
        reverse("educators:student_password_reset", kwargs={"student_id": educator2.id}),
        {
            "password1": '987987',
            "password2": '987987',
        }
    )
    assert response.status_code == 404

@pytest.mark.django_db
def test_change_student_password_sends_signal(client):
    handler = mock.MagicMock()
    signal = signals.member_password_changed
    signal.connect(handler)

    educator = EducatorFactory(username='ed', password='123123')
    student = StudentFactory(username='student', password='123123')
    membership = MembershipFactory(members=[educator, student])
    client.login(username='ed', password='123123')
    response = client.post(
        reverse("educators:student_password_reset", kwargs={"student_id": student.id}),
        {
            "password1": '987987',
            "password2": '987987',
        }
    )

    handler.assert_called_once()
