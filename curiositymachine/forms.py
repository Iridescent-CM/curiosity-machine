from django import forms
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget
from curiositymachine.widgets import FilePickerPickWidget
from django.utils.timezone import now
from django.contrib.auth import get_user_model
from profiles.models import UserRole
import re

User = get_user_model()

MIMETYPE_SCRIPT = """
    evt = arguments[0];
    if (evt.fpfile)
        $('#{}').val(evt.fpfile.mimetype);
"""

class MediaURLField(forms.fields.MultiValueField):
    """
    A field for use with FilePickerPickWidget, which returns both media URL and
    mimetype information.
    """
    #TODO: validate mimetype from the widget against the value provided as an argument.
    #      for now this is used with a filepicker widget that enforces the mimetype, so this
    #      isn't crucial

    widget = FilePickerPickWidget

    def __init__(self, mimetypes='*/*', *args, **kwargs):
        # mimetypes -- comma-separated list of acceptable mimetypes
        self.mimetypes = mimetypes
        fields = (
            forms.URLField(),
            forms.CharField(),
            forms.CharField()
        )
        super(MediaURLField, self).__init__(fields=fields, *args, **kwargs)

    def widget_attrs(self, widget):
        attrs = {
            'data-mimetypes': self.mimetypes
        }
        return attrs

    def compress(self, data_list):
        if data_list:
            return {
                "url": data_list[0],
                "mimetype": data_list[1],
                "filename": data_list[2],
            }
        return {}

class AnalyticsForm(forms.Form):
    today = now()
    start_date = forms.DateField(widget=SelectDateWidget(years=range(2014, today.year + 1)))
    end_date = forms.DateField(widget=SelectDateWidget(years=range(2014, today.year + 1)))

def validate_users_exist(recipients):
    existing = User.objects.filter(
        username__in=recipients,
        extra__role=UserRole.student.value
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

class SignupExtraForm(forms.Form):

    source = forms.CharField(
        required=False,
        widget=forms.HiddenInput
    )

    def signup(self, request, user):
        source = self.cleaned_data.get('source')
        if source:
            user.extra.source = source
            user.extra.save()
