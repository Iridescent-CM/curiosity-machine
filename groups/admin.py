from django.contrib import admin
from . import models

class InvitedInline(admin.TabularInline):
    model = models.Group.invited_users.through
    extra = 1

class UserInline(admin.TabularInline):
    model = models.Group.member_users.through
    extra = 1

class GroupAdmin(admin.ModelAdmin):
    model = models.Group
    list_display = ('name', 'code', 'owners', 'cities')
    fields = ('name','code',)
    readonly_fields = ('code',)
    inlines = (UserInline, InvitedInline, )
    search_fields = ['name', 'code']

    def owners(self, obj):
        return ", ".join(str(owner) for owner in obj.owners())

    def cities(self, obj):
        return ", ".join(owner.profile.city for owner in obj.owners())

class InvitationAdmin(admin.ModelAdmin):
    model = models.Invitation
    list_display = ['id', 'group', 'user']

class MembershipAdmin(admin.ModelAdmin):
    model = models.Membership
    list_display = ['group', 'user', 'role']
    list_filter = ['role']
    search_fields = ['group__name', 'user__username']

# This app is deprecated but not ready for full removal. This removes it from the
# admin, and the whole app should go away before long.
#
#admin.site.register(models.Group, GroupAdmin)
#admin.site.register(models.Invitation, InvitationAdmin)
#admin.site.register(models.Membership, MembershipAdmin)
