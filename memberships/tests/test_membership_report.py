import pytest
from io import StringIO

from ..reports import *

from ..factories import *
from profiles.factories import *
from challenges.factories import *

@pytest.mark.django_db
def test_report_output():
    educators = EducatorFactory.create_batch(3)
    students = StudentFactory.create_batch(4)
    challenges = ChallengeFactory.create_batch(10)
    membership = MembershipFactory(members=educators+students, challenges=challenges)

    output = StringIO()
    MembershipReport(membership).write(output)
    out = output.getvalue()
    print(out)

    assert "educators" in out
    assert "id,username,email,first_name,last_name" in out
    for e in educators:
        assert "%s,%s,%s,%s,%s" % (e.id, e.username, e.email, e.first_name, e.last_name) in out

    assert "students" in out
    assert "id,username,email,first_name,last_name" in out
    for s in students:
        assert "%s,%s,%s,%s,%s" % (s.id, s.username, s.email, s.first_name, s.last_name) in out

    assert "challenges" in out
    assert "id,name" in out
    for c in challenges:
        assert "%s,%s" % (c.id, c.name) in out

@pytest.mark.django_db
def test_submission_count_per_challenge():
    students = StudentFactory.create_batch(4)
    challenges = ChallengeFactory.create_batch(10)
    ProgressFactory(student=students[0], challenge=challenges[0], comment=1)
    ProgressFactory(student=students[0], challenge=challenges[1], comment=5)
    ProgressFactory(student=students[1], challenge=challenges[1], comment=5)
    membership = MembershipFactory(members=students, challenges=challenges)

    output = StringIO()
    MembershipReport(membership).write(output)
    out = output.getvalue()
    print(out)

    assert "%s,%s,1" % (challenges[0].id, challenges[0].name) in out
    assert "%s,%s,2" % (challenges[1].id, challenges[1].name) in out

@pytest.mark.django_db
def test_submission_count_per_student():
    students = StudentFactory.create_batch(4)
    challenges = ChallengeFactory.create_batch(10)
    ProgressFactory(student=students[0], challenge=challenges[0], comment=1)
    ProgressFactory(student=students[0], challenge=challenges[1], comment=5)
    ProgressFactory(student=students[1], challenge=challenges[1], comment=5)
    membership = MembershipFactory(members=students, challenges=challenges)

    output = StringIO()
    MembershipReport(membership).write(output)
    out = output.getvalue()
    print(out)

    assert "%s,,,1" % students[1].email in out
    assert "%s,,,2" % students[0].email in out

@pytest.mark.django_db
def test_dialect_and_line_terminators():
    output = StringIO()
    MembershipReport(MembershipFactory(), dialect="excel").write(output)
    out = output.getvalue()
    print(out)
    assert "\r\n" in out

    output = StringIO()
    MembershipReport(MembershipFactory(), dialect="unix").write(output)
    out = output.getvalue()
    print(out)
    assert "\n" in out
    assert "\r" not in out

def test_build_path():
    assert MembershipReport.build_path(1, filename='name.csv') == '/memberships/1/reports/name.csv'

def test_path_and_filename_properties():
    membership = MembershipFactory.build(id=5, name='membership name')
    report = MembershipReport(membership)
    assert report.filename == 'membership-name.csv'
    assert report.path == '/memberships/5/reports/membership-name.csv'
