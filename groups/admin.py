from django.contrib import admin
from django.contrib.auth.models import User
from .models import Group

class UserInline(admin.TabularInline):
    model = Group.member_users.through
    extra = 1

class GroupAdmin(admin.ModelAdmin):
    model = Group
    list_display = ('name', 'code',)
    fields = ('name',)
    inlines = (UserInline,)

admin.site.register(Group, GroupAdmin)
