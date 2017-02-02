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
