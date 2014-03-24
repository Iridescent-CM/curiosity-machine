from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    raw_id_fields = ('user',)
    search_fields = ['=user__username']


admin.site.register(Profile, ProfileAdmin)
