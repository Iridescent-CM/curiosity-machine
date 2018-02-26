from django.contrib import admin
from .models import *

class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ['account', 'first_name', 'last_name', 'family_role']
    search_fields = ['account__username', 'first_name', 'last_name']
    raw_id_fields = ['image']

admin.site.register(FamilyMember, FamilyMemberAdmin)
