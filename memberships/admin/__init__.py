from django.contrib import admin
from memberships.models import Membership, Member, MemberLimit

class MemberLimitInline(admin.TabularInline):
    model = MemberLimit
    extra = 1
    fields = ('membership', 'role', 'limit', 'current')
    readonly_fields = ('current',)

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration')
    search_fields = ('name',)
    inlines = [MemberLimitInline]
    filter_horizontal = ['challenges']

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')
    search_fields = ('membership__name', 'user__username')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
