from django.contrib import admin
from videos.models import Video, EncodedVideo
from django import forms
from curiositymachine.forms import FilePickerURLField
from django.conf import settings

class VideoAdminForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('source_url',)
    
    def __init__(self, *args, **kwargs):
        super(VideoAdminForm, self).__init__(*args, **kwargs)
        self.fields['source_url'] = FilePickerURLField(mimetypes="video/*", openTo='VIDEO', services='VIDEO,COMPUTER')
        

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

if settings.DEBUG:
    admin.site.register(Video, VideoAdmin)
    admin.site.register(EncodedVideo)
