from django.contrib import admin
from videos.models import Video, EncodedVideo
from django import forms
from curiositymachine.widgets import FilePickerVideoPickWidget
from django.conf import settings

class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('source_url',)
        widgets = {
            'source_url': FilePickerVideoPickWidget(attrs={
                'data-fp-services': 'VIDEO,COMPUTER',
                'data-fp-opento': 'COMPUTER'
            })
        }

class VideoAdmin(admin.ModelAdmin):
    fields = ('source_url',)
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return VideoAdminForm
        else:
            return super(VideoAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.fetch_from_source()

admin.site.register(Video, VideoAdmin)
admin.site.register(EncodedVideo)
