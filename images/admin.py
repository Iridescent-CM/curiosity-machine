from django.contrib import admin
from django import forms
from .models import Image
from cmcomments.forms import FilePickerURLField
import django_rq

class ImageAdminForm(forms.ModelForm):
    class Meta:
        model = Image
    
    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['source_url'] = FilePickerURLField(mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)
        

class ImageAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return ImageAdminForm
        else:
            return super(ImageAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        Image.from_source_with_job(obj.source_url)

admin.site.register(Image, ImageAdmin)
