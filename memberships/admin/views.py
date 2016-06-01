from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from memberships.models import Membership
from memberships.admin.forms import ImportForm

class ImportView(FormView):
    template_name = "memberships/admin/import_members/form.html"
    form_class = ImportForm

    extra_context = {}

    def dispatch(self, request, *args, **kwargs):
        self.membership = get_object_or_404(Membership, id=kwargs.get('id'))
        return super(ImportView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)

        form = self.get_form()
        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})

        context.update(
            self.extra_context,
            original = self.membership,
            adminform = adminForm
        )
        return context

    def form_valid(self, form):
        url = reverse("admin:process_member_import", kwargs={
            "id": self.membership.id
        })
        return HttpResponseRedirect("%s?%s=%s" % (url, "csv", form.cleaned_data["csv_file"]))

