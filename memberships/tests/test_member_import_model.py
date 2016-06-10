import pytest
from mock import Mock

from memberships.factories import MembershipFactory

from memberships.models import member_import_csv_validator, MemberImport

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

def test_member_import_csv_validator_limits_size():
    f = SimpleUploadedFile.from_dict({
        "filename": "file.csv",
        "content": b'file body'
    })
    mockFile = Mock(wraps=f)
    mockFile.size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE + 1

    with pytest.raises(ValidationError) as err:
        member_import_csv_validator(mockFile)

    assert "too large" in str(err.value)

def test_member_import_csv_validator_fails_on_non_utf8():
    f = SimpleUploadedFile.from_dict({
        "filename": "file.csv",
        "content": "file body".encode('utf-16')
    })

    with pytest.raises(ValidationError) as err:
        member_import_csv_validator(f)

    assert "UTF-8" in str(err.value)

def test_member_import_csv_validator_fails_on_unsniffable_csv():
    f = SimpleUploadedFile.from_dict({
        "filename": "file.csv",
        "content": b'' # empty files seem to be unsniffable
    })

    with pytest.raises(ValidationError) as err:
        member_import_csv_validator(f)

    assert "Not a valid CSV" in str(err.value)
