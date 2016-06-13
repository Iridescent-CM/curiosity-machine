import pytest
from mock import Mock, MagicMock, call

from tempfile import TemporaryFile

from memberships.importer import BulkImporter, Result

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

def test_valid_data_written_to_output_without_errors():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,"

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

def test_invalid_data_written_to_output_with_errors():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = False
    MockFormClass().errors = {'1': ['Error desc1', 'Error desc2'], '2': ['Error desc']}

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,1: Error desc1 Error desc2 2: Error desc"

def test_save_exception_written_to_output_with_data():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True
    MockFormClass().save.side_effect = Exception("Boom")

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,Exception encountered while saving record"

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

def test_result_output_includes_header():
    with TemporaryFile(mode='w+t') as fout:
        result = Result(fout)
        result.saved({"a": "1", "b": "2"})

        fout.seek(0)
        assert fout.read().strip().startswith("a,b,errors")

def test_result_saved_outputs_data():
    with TemporaryFile(mode='w+t') as fout:
        result = Result(fout)
        result.saved({"a": "1", "b": "2"})
        result.saved({"a": "3", "b": "4"})

        fout.seek(0)
        assert fout.read().strip() == "a,b,errors\n1,2,\n3,4,"

def test_result_saved_does_not_accept_errors_column():
    with pytest.raises(Exception) as e, TemporaryFile(mode='w+t') as fout:
        result = Result(fout)
        result.saved({"a": "1", "b": "2", "errors": "yep"})
    
    assert str(e.value) == 'errors is a reserved fieldname'

def test_result_invalid_outputs_data_and_errors():
    with TemporaryFile(mode='w+t') as fout:
        result = Result(fout)
        result.invalid({"a": "1", "b": "2"}, {"error 1": ["error"]})

        fout.seek(0)
        assert fout.read().strip() == "a,b,errors\n1,2,error 1: error"

def test_result_save_exception_outputs_data_and_exception_notice():
    with TemporaryFile(mode='w+t') as fout:
        result = Result(fout)
        e = Exception("boom")
        result.save_exception({"a": "1", "b": "2"}, e)

        fout.seek(0)
        assert fout.read().strip() == "a,b,errors\n1,2,Exception encountered while saving record"

def test_result_unsaved_outputs_data():
    with TemporaryFile(mode='w+t') as fout:
        result = Result(fout)
        result.unsaved({"a": "1", "b": "2"})

        fout.seek(0)
        assert fout.read().strip() == "a,b,errors\n1,2,"
