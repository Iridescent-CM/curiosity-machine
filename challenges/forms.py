from django import forms
from django_bleach.forms import BleachField
from django.conf import settings

class MaterialsForm(forms.Form):
    materials = BleachField(required=True,
                        allowed_tags=settings.BLEACH_ALLOWED_TAGS,
                        allowed_attributes=settings.BLEACH_LIB_ATTRIBUTES,
                        allowed_styles=settings.BLEACH_ALLOWED_STYLES)

    def __init__(self, *args, **kwargs):
        progress = kwargs.pop('progress')
        super(MaterialsForm, self).__init__(*args, **kwargs)
        self.fields['materials'].initial = progress.materials_list
