from django.contrib import admin
from memberships.models import Membership, Member, MemberLimit

class MemberLimitInline(admin.TabularInline):
    model = MemberLimit
    extra = 1

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration')
    inlines = [MemberLimitInline]

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
