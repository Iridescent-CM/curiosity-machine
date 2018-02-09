from django.core.exceptions import ValidationError
from django.forms import ModelForm, widgets
from .models import Location

class LocationForm(ModelForm):
    class Media:
        js = ('js/location-form.js',)

    class Meta:
        model = Location
        exclude = []
        widgets = {
            "city": widgets.TextInput
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('country', None) == 'US':
            if cleaned_data.get('state', None) == None:
                self.add_error(
                    'state',
                    ValidationError(
                        'This field is required',
                        code='required'
                    )
                )
        else:
            cleaned_data['state'] = None
        return cleaned_data

    def save(self, commit=True):
        if not commit:
            raise NotImplementedError('LocationForm uses get_or_create and must commit')

        loc, created = Location.objects.get_or_create(**self.cleaned_data)
        return loc
