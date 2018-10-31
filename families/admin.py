from django.contrib import admin
from .models import *

class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['account', 'first_name', 'last_name', 'family_role']
    search_fields = ['account__username', 'first_name', 'last_name']
    raw_id_fields = ['image']

class AwardForceIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'email', 'created_at']
    readonly_fields = ['user', 'email', 'slug', 'created_at']

admin.site.register(FamilyMember, FamilyMemberAdmin)
admin.site.register(AwardForceIntegration, AwardForceIntegrationAdmin)
