from django.contrib import admin
from django.contrib.auth.models import User
from . import models

class InvitedInline(admin.TabularInline):
    model = models.Group.invited_users.through
    extra = 1

class UserInline(admin.TabularInline):
    model = models.Group.member_users.through
    extra = 1

class GroupAdmin(admin.ModelAdmin):
    model = models.Group
    list_display = ('name', 'code',)
    fields = ('name','code',)
    readonly_fields = ('code',)
    inlines = (UserInline, InvitedInline, )

admin.site.register(models.Group, GroupAdmin)
admin.site.register(models.Invitation)
