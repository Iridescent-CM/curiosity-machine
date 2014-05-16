from django import forms
from django_summernote.widgets import SummernoteWidget

class MaterialsForm(forms.Form):
    materials = forms.CharField(required=True, widget=SummernoteWidget())

    def __init__(self, *args, **kwargs):
        progress = kwargs.pop('progress')
        super(MaterialsForm, self).__init__(*args, **kwargs)
        self.fields['materials'].initial = progress.get_materials_list()
        
