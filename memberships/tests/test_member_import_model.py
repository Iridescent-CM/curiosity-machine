import pytest
from mock import Mock

from memberships.models import member_import_csv_validator

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

def test_member_import_csv_validator_fails_on_multiple_chunks():
    f = SimpleUploadedFile.from_dict({
        "filename": "file.csv",
        "content": b'file body'
    })
    mockFile = Mock(wraps=f)
    mockFile.multiple_chunks.return_value = True

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
