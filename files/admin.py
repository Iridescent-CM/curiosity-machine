from django.contrib import admin
from django import forms
from .models import File
from curiositymachine.forms import FilePickerDragDropField
from django.conf import settings

class FileAdminForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ('source_url',)

    def __init__(self, *args, **kwargs):
        super(FileAdminForm, self).__init__(*args, **kwargs)
        self.fields['source_url'] = FilePickerDragDropField(services='COMPUTER')

class FileAdmin(admin.ModelAdmin):
    fields = ('source_url',)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return FileAdminForm
        else:
            return super(FileAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.fetch_from_source()

admin.site.register(File, FileAdmin)
