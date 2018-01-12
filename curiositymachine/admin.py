from django.contrib import admin
from django_summernote.settings import get_attachment_model

admin.site.site_header = 'Curiosity Machine admin'
admin.site.site_title = 'Curiosity Machine admin'

admin.site.unregister(get_attachment_model())