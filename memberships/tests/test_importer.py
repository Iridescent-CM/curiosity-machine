import pytest
from mock import Mock, MagicMock, call, patch, sentinel

from tempfile import TemporaryFile
from django import forms

from memberships.importer import BulkImporter, Status, ResultRow

class ExampleForm(forms.Form):
    a = forms.IntegerField()
    b = forms.IntegerField()
    c = forms.IntegerField()


def test_row_data_validity_checked_by_formclass():
    MockFormClass = MagicMock()

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        assert call({'1':'a', '2':'b', '3':'c'}) in MockFormClass.call_args_list
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

def test_extra_form_kwargs_passed_to_form():
    MockFormClass = MagicMock(spec=ExampleForm)

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'a,b,c\n1,2,3')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass, extra1=1, extra2=2)
        strategy.call(fin, fout)

        for call_args in MockFormClass.call_args_list:
            assert call_args[1] == {'extra1': 1, 'extra2': 2}

def test_valid_data_processed_without_errors():
    MockFormClass = MagicMock(spec=ExampleForm)
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'a,b,c\n1,2,3')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "a,b,c,errors\n1,2,3,"
        assert result["statuses"] == {Status.saved: 1}

def test_output_field_order_matches_input_field_order():
    MockFormClass = MagicMock(spec=ExampleForm)
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'c,a,b\n1,2,3')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "c,a,b,errors\n1,2,3,"

def test_error_column_blanked_out_if_input_has_column_value_but_record_is_valid():
    MockFormClass = MagicMock(spec=ExampleForm)
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'a,b,c,errors\n1,2,3,error!')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "a,b,c,errors\n1,2,3,"

def test_even_fields_not_in_form_written_to_output():
    MockFormClass = MagicMock(spec=ExampleForm)
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'a,b,c,d,e\n1,2,3,4,5')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "a,b,c,d,e,errors\n1,2,3,4,5,"

def test_invalid_data_processed_with_errors():
    MockFormClass = MagicMock(spec=ExampleForm)
    MockFormClass().is_valid.return_value = False
    MockFormClass().errors = {'a': ['Error desc1', 'Error desc2'], 'b': ['Error desc']}

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'a,b,c\n1,2,3')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "a,b,c,errors\n1,2,3,a: Error desc1 Error desc2 b: Error desc"
        assert result["statuses"] == {Status.invalid: 1}

def test_save_exception_processed_with_data():
    MockFormClass = MagicMock(spec=ExampleForm)
    MockFormClass().is_valid.return_value = True
    MockFormClass().save.side_effect = Exception("Boom")

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        fout.seek(0)
        assert fout.read().strip() == "1,2,3,errors\na,b,c,Exception encountered while saving record"
        assert result["statuses"] == {Status.exception: 1}

def test_all_saved_rows_results_in_saved():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c\nd,e,f\ng,h,i')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        assert result["statuses"] == {
            Status.saved: 3
        }
        assert result["final"] == Status.saved

def test_invalid_row_results_in_unsaved_rows():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.side_effect = [True, False, True]

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c\nd,e,f\ng,h,i')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        assert result["statuses"] == {
            Status.unsaved: 2,
            Status.invalid: 1
        }
        assert result["final"] == Status.invalid

def test_exception_row_results_in_partial_save():
    MockFormClass = MagicMock()
    MockFormClass().is_valid.return_value = True
    MockFormClass().save.side_effect = [None, Exception("Boom"), None]

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'1,2,3\na,b,c\nd,e,f\ng,h,i')
        fin.seek(0)

        strategy = BulkImporter(MockFormClass)
        result = strategy.call(fin, fout)

        assert result["statuses"] == {
            Status.saved: 2,
            Status.exception: 1
        }
        assert result["final"] == Status.exception

from django.forms.models import modelform_factory
from django.contrib.auth import get_user_model
User = get_user_model()

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
def test_some_records_saved_when_late_validation_error_happens():
    UserForm = modelform_factory(User, fields=['username', 'email'])

    with TemporaryFile() as fin, TemporaryFile(mode='w+t') as fout:
        fin.write(b'username,email\na,a@example.com\nb,b@example.com\na,a_again@example.com')
        fin.seek(0)

        strategy = BulkImporter(UserForm)
        strategy.call(fin, fout)

        fout.seek(0)
        assert set(User.objects.all().values_list('username', flat=True)) == set(['a', 'b'])
        assert "A user with that username already exists" in fout.read()

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

def test_fieldlabels_to_fieldnames():
    class ExampleForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'password']
            labels = {
                'username': 'User Name',
                'password': 'Their Password'
            }

    importer = BulkImporter(ExampleForm)
    assert importer.fieldlabels_to_fieldnames({
        'User Name': 'exampleuser',
        'Their Password': '123123',
    }) == {
        'username': 'exampleuser',
        'password': '123123',
    }

def test_fieldlabels_to_fieldnames_passes_non_labels_through_unchanged():
    class ExampleForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'password', 'first_name']
            labels = {
                'username': 'User Name',
                'password': 'Their Password',
            }

    importer = BulkImporter(ExampleForm)
    assert importer.fieldlabels_to_fieldnames({
        'User Name': 'exampleuser',
        'Their Password': '123123',
        'first_name': 'example',
        'not a field': 'whatever'
    }) == {
        'username': 'exampleuser',
        'password': '123123',
        'first_name': 'example',
        'not a field': 'whatever'
    }

def test_fieldnames_to_fieldlabels():
    class ExampleForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username', 'password']
            labels = {
                'username': 'User Name',
                'password': 'Their Password'
            }

    importer = BulkImporter(ExampleForm)
    assert importer.fieldnames_to_fieldlabels({
        'username': 'exampleuser',
        'password': '123123',
    }) == {
        'User Name': 'exampleuser',
        'Their Password': '123123',
    }
    assert importer.fieldnames_to_fieldlabels(['username', 'password']) == ['User Name', 'Their Password']

def test_fieldnames_to_fieldlabels_maps_fields_to_auto_labels():
    class ExampleForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['first_name']

    importer = BulkImporter(ExampleForm)
    assert importer.fieldnames_to_fieldlabels({
        'first_name': 'example'
    }) == {
        'First name': 'example'
    }

def test_fieldnames_to_fieldlabels_passes_non_fieldnames_through_unchanged():
    class ExampleForm(forms.ModelForm):
        class Meta:
            model = User
            fields = ['username']

    importer = BulkImporter(ExampleForm)
    assert importer.fieldnames_to_fieldlabels({
        'username': 'exampleuser',
        'whatever': 'whatever',
    }) == {
        'Username': 'exampleuser',
        'whatever': 'whatever'
    }
