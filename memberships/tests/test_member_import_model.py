import pytest
from mock import patch

from memberships.factories import MembershipFactory

from memberships.models import MemberImport

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from django.conf import settings
from django.utils.timezone import now
from django_rq import get_worker, get_queue
from django_s3_storage.storage import S3Storage
from datetime import timedelta

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
