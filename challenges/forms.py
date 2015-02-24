from django import forms
from django_bleach.forms import BleachField
from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms import TextInput

class MaterialsForm(forms.Form):
    materials = BleachField(required=True,
                        allowed_tags=settings.BLEACH_ALLOWED_TAGS,
                        allowed_attributes=settings.BLEACH_LIB_ATTRIBUTES,
                        allowed_styles=settings.BLEACH_ALLOWED_STYLES)

    def __init__(self, *args, **kwargs):
        progress = kwargs.pop('progress')
        super(MaterialsForm, self).__init__(*args, **kwargs)
        self.fields['materials'].initial = progress.materials_list

class ThemeForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'icon', 'color']
        widgets = {
            'name': TextInput,
            'icon': TextInput,
            'color': TextInput
        }

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color[0] != '#':
            color = '#' + color
        return color

class FilterForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'color', 'visible']

    def clean_color(self):
        color = self.cleaned_data.get('color')
        if color[0] != '#':
            color = '#' + color
        return color