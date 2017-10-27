from django.contrib import admin
from django_summernote.settings import get_attachment_model

admin.site.unregister(get_attachment_model())