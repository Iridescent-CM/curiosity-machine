from django.contrib import admin
from .models import *

class PermissionSlipAdmin(admin.ModelAdmin):
    model = PermissionSlip
    list_display = ('id', 'signature', 'created_at', 'account')
    readonly_fields = ('signature', 'created_at', 'account')

admin.site.register(PermissionSlip, PermissionSlipAdmin)
