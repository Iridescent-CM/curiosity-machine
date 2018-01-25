from django.contrib import admin
from enumfields.admin import EnumFieldListFilter
from .models import *

class SignatureAdmin(admin.ModelAdmin):
    list_display = ['id', 'template_id', 'user', 'status', 'created_at', 'updated_at']
    list_filter = [('status', EnumFieldListFilter)]
    readonly_fields = ['id', 'template_id', 'user', 'created_at', 'updated_at']
    search_fields = ['id', 'template_id', 'user__username']

admin.site.register(Signature, SignatureAdmin)
