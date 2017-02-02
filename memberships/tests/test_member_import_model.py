import pytest
from mock import patch

from memberships.factories import MembershipFactory

from memberships.models import MemberImport, Membership
from memberships.importer import Status

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.timezone import now
from django_rq import get_worker, get_queue
from django_s3_storage.storage import S3Storage
from datetime import timedelta
import os

def test_output_name():
    assert MemberImport.output_name("a/b/c/file.ext") == "a/b/c/file_result.ext"

@pytest.mark.django_db
def test_saving_a_new_member_import_processes_the_input_file_in_a_worker():
    queue = get_queue()
    queue.empty()

    membership = MembershipFactory()
    member_import = MemberImport(input=SimpleUploadedFile("file.csv", b'file contents'), membership=membership)
    member_import.save()

    assert queue.count == 1
    assert not MemberImport.objects.all().first().output.name

    get_worker().work(burst=True)

    assert MemberImport.objects.all().first().output.name

@pytest.mark.django_db
def test_member_import_lifecycle_with_s3():
    with patch("django.core.files.storage.default_storage._wrapped", S3Storage()) as storage:
        queue = get_queue()
        queue.empty()

        membership = MembershipFactory()
        member_import = MemberImport(input=SimpleUploadedFile("file.csv", b'file contents'), membership=membership)
        member_import.save()
        get_worker().work(burst=True)

        result = MemberImport.objects.all().first()
        assert storage.exists(result.output.name)
        assert storage.exists(result.input.name)

@pytest.mark.django_db
def test_member_import_deletion_deletes_files():
    queue = get_queue()
    queue.empty()

    membership = MembershipFactory()
    member_import = MemberImport(input=SimpleUploadedFile("file.csv", b'file contents'), membership=membership)
    member_import.save()
    get_worker().work(burst=True)

    saved = MemberImport.objects.all().first()
    assert default_storage.exists(saved.input.name)
    assert default_storage.exists(saved.output.name)

    saved.delete()

    assert not default_storage.exists(saved.input.name)
    assert not default_storage.exists(saved.output.name)

@pytest.mark.django_db
def test_stale_objects_manager():
    membership = MembershipFactory()
    stale = MemberImport.objects.create(
        input = SimpleUploadedFile("file.csv", b'file contents'),
        membership = membership
    )
    MemberImport.objects.create(
        input = SimpleUploadedFile("file.csv", b'file contents'),
        membership = membership
    )
    too_old = now() - timedelta(days=settings.MEMBER_IMPORT_EXPIRATION_DAYS + 1)
    MemberImport.objects.filter(pk=stale.pk).update(updated_at=too_old)

    assert MemberImport.objects.count() == 2
    assert MemberImport.stale_objects.count() == 1
    assert MemberImport.stale_objects.first().id == stale.id

@pytest.mark.django_db
def test_stale_manager_older_than():
    membership = MembershipFactory()
    MemberImport.objects.create(
        input = SimpleUploadedFile("file.csv", b'file contents'),
        membership = membership
    )
    default_days = settings.MEMBER_IMPORT_EXPIRATION_DAYS
    MemberImport.objects.all().update(
        updated_at = now() - timedelta(days=default_days + 1)
    )
    MemberImport.objects.create(
        input = SimpleUploadedFile("file2.csv", b'file contents'),
        membership = membership
    )

    assert MemberImport.objects.count() == 2
    assert MemberImport.stale_objects.older_than().count() == 1
    assert MemberImport.stale_objects.older_than(default_days).count() == 1
    assert MemberImport.stale_objects.older_than(default_days + 2).count() == 0

def test_stale_objects_threshold():
    default = settings.MEMBER_IMPORT_EXPIRATION_DAYS
    def roughly_equal(d1, d2):
        return d1 - d2 < timedelta(minutes=5)

    assert roughly_equal(
        MemberImport.stale_objects.threshold(),
        now() - timedelta(days=default)
    )
    assert roughly_equal(
        MemberImport.stale_objects.threshold(4),
        now() - timedelta(days=4)
    )

@pytest.mark.django_db
def test_unexpected_exception_recorded_in_status():
    queue = get_queue()
    queue.empty()

    membership = MembershipFactory()
    member_import = MemberImport(input=SimpleUploadedFile("file.csv", b'file contents'), membership=membership)
    member_import.save()
    with patch("memberships.importer.BulkImporter.call") as mock:
        mock.side_effect = Exception("kaboom")
        get_worker().work(burst=True)

    saved = MemberImport.objects.all().first()
    assert Status(saved.status) == Status.exception
