from django.contrib import admin
from memberships.models import Membership, Member

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration')

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
