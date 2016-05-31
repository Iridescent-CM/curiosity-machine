from django.contrib import admin
from django.http import HttpResponse
from django.conf.urls import url
from django.shortcuts import get_object_or_404
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

    def get_urls(self):
        urls = super(MembershipAdmin, self).get_urls()
        extra_urls = [
            url(r'^(?P<id>\d+)/import_members/$', self.admin_site.admin_view(self.import_members), name="import_members"),
        ]
        return extra_urls + urls

    def import_members(self, request, *args, **kwargs):
        obj = get_object_or_404(Membership, id=kwargs.get('id'))
        return HttpResponse('OK')

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')
    search_fields = ('membership__name', 'user__username')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
