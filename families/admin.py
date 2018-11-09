from django.contrib import admin
from .models import *

class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['account', 'first_name', 'last_name', 'family_role']
    search_fields = ['account__username', 'first_name', 'last_name']
    raw_id_fields = ['image']

class AwardForceIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'created_at', 'last_used']
    readonly_fields = ['user', 'email', 'slug', 'created_at', 'last_used']

class PermissionSlipAdmin(admin.ModelAdmin):
    list_display = ['id', 'signature', 'created_at', 'account']
    readonly_fields = ['signature', 'created_at', 'account']

admin.site.register(FamilyMember, FamilyMemberAdmin)
admin.site.register(AwardForceIntegration, AwardForceIntegrationAdmin)
admin.site.register(PermissionSlip, PermissionSlipAdmin)
