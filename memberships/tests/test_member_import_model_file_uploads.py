import pytest
from django_rq import get_worker, get_queue

from memberships.factories import MembershipFactory
from memberships.importer import Status
from django.contrib.auth import get_user_model
User = get_user_model()

from memberships.models import MemberImport, Membership

from django.core.files.uploadedfile import SimpleUploadedFile
from datetime import date
import os

# It's useful to have actual files for some number of tests. They can be used
# in manual QA, or be the basis for QA test files, and it's then best to ensure
# they are valid or invalid as expected.

@pytest.mark.django_db
def test_valid_example_file():
    queue = get_queue()
    queue.empty()

    membership = MembershipFactory()
    with open("%s/data/good.csv" % os.path.dirname(os.path.abspath(__file__)), mode='rb') as fp:
        member_import = MemberImport(input=SimpleUploadedFile("file.csv", fp.read()), membership=membership)
    member_import.save()
    get_worker().work(burst=True)

    member_import = MemberImport.objects.all().first()
    assert Status(member_import.status) == Status.saved

    membership = Membership.objects.all().first()
    assert membership.members.count() > 0

@pytest.mark.django_db
def test_file_with_extra_columns_can_be_valid():
    queue = get_queue()
    queue.empty()

    membership = MembershipFactory()
    with open("%s/data/extra.csv" % os.path.dirname(os.path.abspath(__file__)), mode='rb') as fp:
        member_import = MemberImport(input=SimpleUploadedFile("file.csv", fp.read()), membership=membership)
    member_import.save()
    get_worker().work(burst=True)

    assert Status(MemberImport.objects.all().first().status) == Status.saved

    user = User.objects.all().first()
    assert user.first_name == "first1"
    assert user.profile.birthday == date(year=1990, day=1, month=1)
    assert not user.profile.title
    assert not user.profile.employer

@pytest.mark.django_db
def test_invalid_example_file():
    queue = get_queue()
    queue.empty()

    membership = MembershipFactory()
    with open("%s/data/bad.csv" % os.path.dirname(os.path.abspath(__file__)), mode='rb') as fp:
        member_import = MemberImport(input=SimpleUploadedFile("file.csv", fp.read()), membership=membership)
    member_import.save()
    get_worker().work(burst=True)

    member_import = MemberImport.objects.all().first()
    assert Status(member_import.status) == Status.invalid

    membership = Membership.objects.all().first()
    assert membership.members.count() == 0


