from django.contrib import admin
from videos.models import Video, EncodedVideo
from django import forms
from curiositymachine.widgets import FilePickerVideoPickWidget
from django.conf import settings
import json

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
    fieldsets = (
        (None, {
            'fields': ('source_url', 'url_link')
        }),
        ('Debug info', {
            'fields': ('job_details',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('url_link', 'job_details')
    list_display = ('id', 'url_link', 'source_url_link')

    def url_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.url, obj.url)
    url_link.allow_tags = True

    def source_url_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.source_url, obj.source_url)
    source_url_link.allow_tags = True

    def job_details(self, obj):
        return '<pre><code>\n%s</code></pre>' % (json.dumps(json.loads(obj.raw_job_details), indent=4, sort_keys=True))
    job_details.allow_tags = True

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
