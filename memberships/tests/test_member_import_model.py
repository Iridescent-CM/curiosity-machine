import pytest

from memberships.factories import MembershipFactory

from memberships.models import MemberImport

from django.core.files.uploadedfile import SimpleUploadedFile
from django_rq import get_worker, get_queue

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
