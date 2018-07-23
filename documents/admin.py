from django.contrib import admin
from django import forms
from .models import Document
from s3direct.widgets import S3DirectWidget
from django.conf import settings

class DocumentAdminForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ('source_url',)
        widgets = {
            'source_url': S3DirectWidget(dest='admin-documents')
        }

class DocumentAdmin(admin.ModelAdmin):
    fields = ('source_url', 'url_link')
    readonly_fields = ('url_link',)
    list_display = ('id', 'url_link', 'source_url_link')

    def url_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.url, obj.url)
    url_link.allow_tags = True

    def source_url_link(self, obj):
        return '<a href="%s">%s</a>' % (obj.source_url, obj.source_url)
    source_url_link.allow_tags = True

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            return DocumentAdminForm
        else:
            return super(DocumentAdmin, self).get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        obj.save()
        obj.fetch_from_source()

admin.site.register(Document, DocumentAdmin)
