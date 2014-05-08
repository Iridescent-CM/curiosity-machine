from django.contrib import admin
from django import forms
from .models import Image
from curiositymachine.forms import FilePickerURLField
from django.conf import settings

class ImageAdminForm(forms.ModelForm):
    fields = ('source_url',)
    
    class Meta:
        model = Image

    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['source_url'] = FilePickerURLField(mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER')

class ImageAdmin(admin.ModelAdmin):
    fields = ('source_url',)

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return ImageAdminForm
        else:
            return super(ImageAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.fetch_from_source()

if settings.DEBUG:
    admin.site.register(Image, ImageAdmin)
