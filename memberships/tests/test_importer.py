import pytest
from mock import Mock, MagicMock, call

from tempfile import TemporaryFile

from memberships.importer import BulkImporter, Status, ResultRow

def test_row_data_validity_checked_by_formclass():
    MockFormClass = MagicMock()

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        assert MockFormClass.call_args == call({'1':'a', '2':'b', '3':'c'})
        assert MockFormClass().is_valid.called

def test_valid_data_calls_form_save():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        assert MockFormClass().save.called

def test_invalid_data_doesnt_call_form_save():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = False

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        assert not MockFormClass().save.called

def test_valid_data_processed_without_errors():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,"
        assert result == {Status.saved: 1}

def test_error_column_blanked_out_if_input_has_column_value_but_record_is_valid():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3,errors\na,b,c,error!')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,"

def test_invalid_data_processed_with_errors():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = False
    MockFormClass().errors = {'1': ['Error desc1', 'Error desc2'], '2': ['Error desc']}

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,1: Error desc1 Error desc2 2: Error desc"
        assert result == {Status.invalid: 1}

def test_save_exception_processed_with_data():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True
    MockFormClass().save.side_effect = Exception("Boom")

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,Exception encountered while saving record"
        assert result == {Status.exception: 1}

def test_invalid_row_results_in_unsaved_rows():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.side_effect = [True, False, True]

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c\nd,e,f\ng,h,i')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        assert result == {
            Status.unsaved: 2,
            Status.invalid: 1
        }

def test_exception_row_results_in_partial_save():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True
    MockFormClass().save.side_effect = [None, Exception("Boom"), None]

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c\nd,e,f\ng,h,i')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        assert result == {
            Status.saved: 2,
            Status.exception: 1
        }

from django.forms.models import modelform_factory
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_no_records_saved_when_invalid_record_exists():
    UserForm = modelform_factory(User, fields=['username', 'email'])

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'username,email\na,a@example.com\nb,b@example.com\n,nousername@example.com')
        fin.seek(0)

        strategy = BulkImporter(UserForm)
        strategy.call(fin, fout)

        assert User.objects.count() == 0

@pytest.mark.django_db
def test_some_records_saved_when_save_exception_happens():
    UserForm = modelform_factory(User, fields=['username', 'email'])

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        # a duplicate username is used to force the save exception, which is maybe something
        # a more sophisticated importer would check for internally
        fin.write(b'username,email\na,a@example.com\nb,b@example.com\na,a_again@example.com')
        fin.seek(0)

        strategy = BulkImporter(UserForm)
        strategy.call(fin, fout)

        fout.seek(0)
        assert set(User.objects.all().values_list('username', flat=True)) == set(['a', 'b'])
        assert "Exception encountered" in fout.read()

def test_resultrow_header():
    row = {"a": "1", "b": "2"}
    assert ResultRow(Status.saved, row).fieldnames == ["a", "b", "errors"]

def test_resultrow_prohibits_reserved_fields_in_data():
    with pytest.raises(Exception) as e:
        ResultRow(Status.saved, {"a": "1", "errors": "yep"})
    assert "cannot use these reserved fieldnames" in str(e.value)

def test_resultrow_fields():
    row = {"a": "1", "b": "2"}
    assert ResultRow(Status.saved, row).fields == {"a": "1", "b": "2"}
    assert ResultRow(Status.invalid, row, "errors message").fields == {"a": "1", "b": "2", "errors": "errors message"}
    assert ResultRow(Status.unsaved, row).fields == {"a": "1", "b": "2"}
    assert ResultRow(Status.exception, row, "exception message").fields == {"a": "1", "b": "2", "errors": "exception message"}

