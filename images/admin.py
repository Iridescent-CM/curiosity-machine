from django.contrib import admin
from django import forms
from .models import Image
from curiositymachine.widgets import FilePickerImagePickWidget
from django.conf import settings

class ImageAdminForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ('source_url',)
        widgets = {
            'source_url': FilePickerImagePickWidget(attrs={
                'data-fp-services': 'WEBCAM,COMPUTER',
                'data-fp-opento': 'COMPUTER'
            })
        }

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

admin.site.register(Image, ImageAdmin)
