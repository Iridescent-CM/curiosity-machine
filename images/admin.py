from django.contrib import admin
from django import forms
from .models import Image
from cmcomments.forms import FilePickerURLField
from images.tasks import upload_filepicker_image
import django_rq

class ImageAdminForm(forms.ModelForm):
    class Meta:
        model = Image
    
    def __init__(self, *args, **kwargs):
        super(ImageAdminForm, self).__init__(*args, **kwargs)
        self.fields['filepicker_url'] = FilePickerURLField(mimetypes="image/*", openTo='WEBCAM', services='WEBCAM,COMPUTER', required=False)
        

class ImageAdmin(admin.ModelAdmin):
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return ImageAdminForm
        else:
            return super(ImageAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        django_rq.enqueue(upload_filepicker_image, obj)

admin.site.register(Image, ImageAdmin)
