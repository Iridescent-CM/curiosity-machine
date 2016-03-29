from django import forms
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget
from curiositymachine.widgets import FilePickerInlineWidget, FilePickerPickWidget
from django.utils.timezone import now
from django.contrib.auth.models import User
import re

MIMETYPE_SCRIPT = """
    evt = arguments[0];
    if (evt.fpfile)
        $('#{}').val(evt.fpfile.mimetype);
"""

class FilePickerField(forms.URLField):
    default_mimetypes = "*/*"
    default_openTo = 'COMPUTER'
    default_services = ''

    def __init__(self, *args, **kwargs):
        self.apikey = kwargs.pop('apikey', settings.FILEPICKER_API_KEY)
        self.mimetypes = kwargs.pop('mimetypes', self.default_mimetypes)
        self.openTo = kwargs.pop('openTo', self.default_openTo)
        self.services = kwargs.pop('services', self.default_services)
        self.mimetype_widget = kwargs.pop('mimetype_widget', None)
        super().__init__(*args, **kwargs)

    def widget_attrs(self, widget):
        attrs = {
            'data-fp-apikey': self.apikey, 
            'data-fp-mimetypes': self.mimetypes, 
            'data-fp-openTo': self.openTo, 
            'data-fp-services': self.services, 
            'data-fp-button-class': 'btn btn-primary'
        }
        if self.mimetype_widget:
            attrs['onchange'] = MIMETYPE_SCRIPT.format(self.mimetype_widget.attrs.get('id'))
        return attrs

class FilePickerURLField(FilePickerField):
    widget = FilePickerInlineWidget
    
class FilePickerMediaField(forms.fields.MultiValueField):
    widget = FilePickerPickWidget

    def __init__(self, *args, **kwargs):
        self.mimetypes = kwargs.pop('mimetypes', '*/*')
        self.openTo = kwargs.pop('openTo', None)
        self.services = kwargs.pop('services', None)
        fields = (
            forms.URLField(),
            forms.CharField()
        )
        super(FilePickerMediaField, self).__init__(fields=fields, *args, **kwargs)

    def widget_attrs(self, widget):
        attrs = {
            'data-fp-mimetypes': self.mimetypes
        }
        if self.openTo:
            attrs['data-fp-opento'] = self.openTo
        if self.services:
            attrs['data-fp-services']= self.services
        return attrs

    def compress(self, data_list):
        if data_list:
            return {
                "url": data_list[0],
                "mimetype": data_list[1]
            }
        return {}

class AnalyticsForm(forms.Form):
    today = now()
    start_date = forms.DateField(widget=SelectDateWidget(years=range(2014, today.year + 1)))
    end_date = forms.DateField(widget=SelectDateWidget(years=range(2014, today.year + 1)))

def validate_users_exist(recipients):
    existing = User.objects.filter(
        username__in=recipients,
        profile__is_student=True
    ).values_list('username', flat=True)
    nonexisting = list(set(recipients) - set(existing))
    if nonexisting:
        raise forms.ValidationError(
            "Found no users named: %(users)s",
            code='nonexistant-user',
            params={'users':', '.join(nonexisting)}
        )

class StudentUsernamesField(forms.Field):
    widget = forms.Textarea
    default_validators = [validate_users_exist]

    def to_python(self, value):
        if not value:
            return []
        return list(val for val in re.split("[\s;,]+", value) if val)