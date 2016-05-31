import csv
from django import forms
from django.contrib import admin
from django.template.response import TemplateResponse
from django.shortcuts import get_object_or_404
from django.conf.urls import url
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.views.generic.edit import FormView
from memberships.models import Membership, Member, MemberLimit

class MemberLimitInline(admin.TabularInline):
    model = MemberLimit
    extra = 1
    fields = ('membership', 'role', 'limit', 'current')
    readonly_fields = ('current',)

def foo(x):
    for row in x:
        yield row.decode('utf-8')

class ImportForm(forms.Form):
    csv_file = forms.FileField(required=True, allow_empty_file=False)

    def clean(self):
        cleaned_data = super(ImportForm, self).clean()
        csv_file = cleaned_data.get('csv_file')
        if csv_file.multiple_chunks():
            raise ValidationError("File too large to process")
        contents = csv_file.read()
        try:
            contents = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise ValidationError("File does not appear to be UTF-8 encoded")
        except:
            raise ValidationError("Unknown error decoding file")

        try:
            dialect = csv.Sniffer().sniff(contents)
        except:
            raise ValidationError("Error determining CSV document dialect")

        reader = csv.DictReader(foo(csv_file))
        for row in reader:
            print("XXX", row.keys())

class ImportView(FormView):
    template_name = "memberships/admin/foo.html"
    form_class = ImportForm
    membership = None

    def get_success_url(self):
        return reverse('admin:memberships_membership_change', args=[self.membership.id])

class MembershipAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'expiration')
    search_fields = ('name',)
    inlines = [MemberLimitInline]
    filter_horizontal = ['challenges']

    def get_urls(self):
        urls = super(MembershipAdmin, self).get_urls()
        my_urls = [
            url(r'^(?P<id>\d+)/import_members/$', self.admin_site.admin_view(self.import_members), name="import_members"),
        ]
        return my_urls + urls

    def import_members(self, request, *args, **kwargs):
        obj = get_object_or_404(Membership, id=kwargs.get('id'))

        response = ImportView.as_view(membership=obj)(request, *args, **kwargs)
        if hasattr(response, 'context_data'):
            response.context_data.update(
                self.admin_site.each_context(request),
                opts = self.model._meta,
                has_change_permission = self.has_change_permission(request, obj),
                original = obj,
            )

        return response
        #obj = get_object_or_404(Membership, id=kwargs.get('id'))
        #context = dict(
        #    self.admin_site.each_context(request),
        #    opts = self.model._meta,
        #    has_change_permission = self.has_change_permission(request, obj),
        #    original = obj,
        #    form = ImportForm()
        #)
        #return TemplateResponse(request, "memberships/admin/foo.html", context)

class MemberAdmin(admin.ModelAdmin):
    list_display = ('id', 'membership', 'user')
    search_fields = ('membership__name', 'user__username')

admin.site.register(Membership, MembershipAdmin)
admin.site.register(Member, MemberAdmin)
