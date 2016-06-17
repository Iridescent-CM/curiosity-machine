import pytest
from mock import Mock
import os

from django.core.files.uploadedfile import SimpleUploadedFile

from memberships.admin.forms import ImportForm

TEST_DIR = os.path.dirname(__file__)

def test_valid_import_form():
    with open(os.path.join(TEST_DIR, './data/good.csv'), 'rb') as fp:
        file_data = {"csv_file": SimpleUploadedFile('file.csv', fp.read())}

    form = ImportForm({}, file_data)
    assert form.is_valid()

def test_import_form_requires_csv_file():
    form = ImportForm({}, {})
    assert not form.is_valid()

def test_import_form_validates_csv_file_is_not_chunked():
    mockFile = Mock(spec=SimpleUploadedFile) 
    mockFile.multiple_chunks.return_value = True
    file_data = {"csv_file": mockFile}

    form = ImportForm({}, file_data)
    assert not form.is_valid()

def test_import_form_validates_utf8_content():
    mockFile = Mock(spec=SimpleUploadedFile) 
    mockFile.multiple_chunks.return_value = False
    mockFile.read.return_value = "contents".encode("utf-16")
    file_data = {"csv_file": mockFile}

    form = ImportForm({}, file_data)
    assert not form.is_valid()
