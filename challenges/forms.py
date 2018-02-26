import bleach

from django import forms
from django.conf import settings
from django.utils.safestring import mark_safe
from django.forms import TextInput
from django_summernote.widgets import SummernoteWidget

class BleachField(forms.CharField):
    widget = SummernoteWidget

    def to_python(self, value):
        """
        Strips any dodgy HTML tags from the input
        """
        return bleach.clean(value,
            tags=[
                'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'h1', 'h2', 'h3', 'h4',
                'br', 'strike', 'li', 'ul', 'div', 'ol', 'span', 'blockquote',
                'pre', 'img'
            ],
            attributes={
                '*': ['title', 'style'],
                'a': [
                    'id', 'href', 'fpfilekey', 'rel', 'class', 'number',
                    'data-height', 'data-width'
                ],
                'img': [
                    'src', 'alt', 'width', 'height', 'data-height','data-width',
                    'data-upload', 'class', 'id', 'data-original', 'data-key'
                ],
                'div' : ['class']
            },
            styles=['font-family', 'font-weight', 'text-decoration', 'font-variant'],
            strip=True,
            strip_comments=True,
        )

class MaterialsForm(forms.Form):
    materials = BleachField(required=True)

    def __init__(self, *args, **kwargs):
        progress = kwargs.pop('progress')
        super(MaterialsForm, self).__init__(*args, **kwargs)
        self.fields['materials'].initial = progress.materials_list

class ThemeForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'icon']
        widgets = {
            'name': TextInput,
            'icon': TextInput,
        }

class FilterForm(forms.ModelForm):
    class Meta:
        fields = ['name', 'visible']