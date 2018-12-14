from django.contrib import admin
from django.contrib.admin.options import InlineModelAdmin
from django.http import HttpResponseRedirect, Http404
from django.conf.urls import url
from django.shortcuts import get_object_or_404
from django.templatetags.static import static
from django.utils.functional import lazy
from django.utils.text import format_lazy
from django.contrib import messages
from django.core.files.storage import default_storage
from memberships.models import *
from memberships.importer import Status
from django.utils.timezone import now
from datetime import timedelta
from .tasks import *

class ExpirationFilter(admin.SimpleListFilter):
    title = 'Expiration'

    parameter_name = 'expiry'

    def lookups(self, request, model_admin):
        return (
            ('expired', 'Expired'),
            ('week', 'Expires within 1 week'),
            ('month', 'Expires within 1 month'),
            ('none', 'No expiration'),
            ('unexpired', 'All unexpired'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        t = now()
        if value == 'expired':
            return queryset.filter(expiration__lt=t)
        elif value == 'week':
            return queryset.exclude(expiration__lt=t).filter(expiration__lt=t + timedelta(weeks=1))
        elif value == 'month':
            return queryset.exclude(expiration__lt=t).filter(expiration__lt=t + timedelta(days=31))
        elif value == 'unexpired':
            return queryset.exclude(expiration__lt=t)
        elif value == 'none':
            return queryset.filter(expiration__isnull=True)

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

class NewMemberImportInline(InlineModelAdmin):
    template = "admin/edit_inline/stacked_with_help_text.html"
    model = MemberImport
    extra = 1
    max_num = 1
    fields = ['input']
    verbose_name = "New import"
    verbose_name_plural = "Import members"
    can_delete = False
    help_text = format_lazy(
        'Creates student users and adds them to this membership. Input file must be csv format, utf-8 encoding. Use <a href="{url}">this template</a>.',
        url=lazy(static, str)('CM_Account_Creation_Template_Aug2016.csv')
    )

    def has_change_permission(self, request):
        return False

class MemberLimitInline(InlineModelAdmin):
    template = "admin/edit_inline/tabular_with_help_text.html"
    model = MemberLimit
    extra = 1
    fields = ('membership', 'role', 'limit', 'current')
    readonly_fields = ('current',)
    help_text = "Set the number of students and educators who can be added to this membership. If the limit is set to 0, no members can be added."

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration', 'is_active')
    list_display_links = ('id', 'name',)
    list_filter = (ExpirationFilter, 'is_active')
    search_fields = ('name',)
    inlines = [MemberLimitInline, NewMemberImportInline, PastMemberImportInline]
    filter_horizontal = ['challenges', 'extra_units']
    change_form_template = 'memberships/admin/change_form.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            url(r'^(?P<object_id>\d+)/report/$',
                self.admin_site.admin_view(self.run_report),
                name="memberships_membership_report"
            ),
            url(r'^(?P<object_id>\d+)/report/(?P<filename>.+)$',
                self.admin_site.admin_view(self.get_report),
                name="memberships_membership_get_report"
            ),
        ]
        return my_urls + urls

    def run_report(self, request, object_id):
        messages.success(request, 'Report link will be emailed to %s' % request.user.email)
        queue_membership_report(object_id, request.user.email)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER','/'))

    def get_report(self, request, object_id, filename):
        filename = MembershipReport.build_path(object_id, filename=filename)
        if default_storage.exists(filename):
            return HttpResponseRedirect(default_storage.url(filename))
        else:
            raise Http404("File not found: %s" % filename)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')
    search_fields = ('membership__name', 'user__username')
    raw_id_fields = ('membership', 'user')

    def get_form(self, request, obj=None, **kwargs):
        kwargs.update({
            'help_texts': {
                'membership': 'Enter a membership ID, or use the magnifying glass to search',
                'user': 'Enter a user ID, or use the magnifying glass to search'
            }
        })
        return super().get_form(request, obj, **kwargs);

class GroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'membership')
    search_fields = ('membership__name', 'name')
    raw_id_fields = ('membership',)

class GroupMemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership_name', 'group_name', 'member_name')
    raw_id_fields = ('group', 'member')

    def membership_name(self, obj):
        return str(obj.group.membership)

    def group_name(self, obj):
        return obj.group.name

    def member_name(self, obj):
        return obj.member.user

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(GroupMember, GroupMemberAdmin)
