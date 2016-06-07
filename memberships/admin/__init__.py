from django.contrib import admin
from django.http import HttpResponse
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from memberships.models import Membership, Member, MemberLimit, MemberImport
from memberships.admin.views import ImportView, ProcessView

class MemberImportInline(admin.TabularInline):
    model = MemberImport
    extra = 0

class MemberLimitInline(admin.TabularInline):
    model = MemberLimit
    extra = 1
    fields = ('membership', 'role', 'limit', 'current')
    readonly_fields = ('current',)

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration')
    search_fields = ('name',)
    inlines = [MemberLimitInline, MemberImportInline]
    filter_horizontal = ['challenges']

    def get_urls(self):
        urls = super(MembershipAdmin, self).get_urls()
        extra_urls = [
            url(r'^(?P<id>\d+)/import_members/$', self.admin_site.admin_view(self.import_members), name="import_members"),
            url(r'^(?P<id>\d+)/import_members/process/$', self.admin_site.admin_view(self.process_import), name="process_member_import"),
        ]
        return extra_urls + urls

    def import_members(self, request, *args, **kwargs):
        context = dict(
            self.admin_site.each_context(request),
            opts = self.model._meta
        )
        return ImportView.as_view(extra_context=context)(request, *args, **kwargs)

    def process_import(self, request, *args, **kwargs):
        context = dict(
            self.admin_site.each_context(request),
            opts = self.model._meta
        )
        return ProcessView.as_view(extra_context=context)(request, *args, **kwargs)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')
    search_fields = ('membership__name', 'user__username')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
