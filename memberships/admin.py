from django.contrib import admin
from django.http import HttpResponse
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from memberships.models import Membership, Member, MemberLimit, MemberImport
from memberships.importer import Status

class PastMemberImportInline(admin.TabularInline):
    model = MemberImport
    extra = 0
    fields = ['input', 'output', 'status_message', 'created_at']
    readonly_fields = ['input', 'output', 'status_message', 'created_at']
    can_delete = False

    messages = {
        None: 'Import pending',
        Status.invalid: 'Invalid records found, no users created',
        Status.saved: 'All users created',
        Status.exception: 'Encountered errors, some users may have been created',
        Status.unsaved: 'No users created'
    }

    def has_add_permission(self, request):
        return False

    def status_message(self, obj):
        key = None
        if obj.status != None:
            key = Status(obj.status)
        return self.messages[key]

class NewMemberImportInline(admin.StackedInline):
    model = MemberImport
    extra = 1
    max_num = 1
    fields = ['input']
    verbose_name = "New import"
    verbose_name_plural = "Import members"
    can_delete = False

    def has_change_permission(self, request):
        return False

class MemberLimitInline(admin.TabularInline):
    model = MemberLimit
    extra = 1
    fields = ('membership', 'role', 'limit', 'current')
    readonly_fields = ('current',)

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration')
    search_fields = ('name',)
    inlines = [MemberLimitInline, NewMemberImportInline, PastMemberImportInline]
    filter_horizontal = ['challenges', 'extra_units']

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')
    search_fields = ('membership__name', 'user__username')
    raw_id_fields = ('membership', 'user',)

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            'help_texts': {
                'membership': 'Enter a membership ID, or use the magnifying glass to search',
                'user': 'Enter a user ID, or use the magnifying glass to search'
            }
        })
        return super().get_form(request, obj, **kwargs);

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
