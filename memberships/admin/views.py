from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views.generic.detail import SingleObjectMixin
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import admin
from django.http import HttpResponseRedirect
from memberships.models import Membership
from memberships.admin.forms import ImportForm

class ExtraContextMixin(object):
    extra_context = {}

    def get_context_data(self, **kwargs):
        context = super(ExtraContextMixin, self).get_context_data(**kwargs)
        context.update(self.extra_context)
        return context

class RequiredObjectMixin(SingleObjectMixin):
    object = None # SingleObjectMixin checks self.object
    attribute_name = None

    def dispatch(self, request, *args, **kwargs):
        """
        Find the required object and put it in its attribute
        """
        setattr(self, self.attribute_name, self.get_object())
        return super(RequiredObjectMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Insert the single object into the context dict.
        Rewrite of SingleObjectMixin.get_context_data to support dynamic attribute name.
        """
        context = {}
        if getattr(self, self.attribute_name):
            context[self.attribute_name] = getattr(self, self.attribute_name)
            context_object_name = self.get_context_object_name(getattr(self, self.attribute_name))
            if context_object_name:
                context[context_object_name] = getattr(self, self.attribute_name)
        context.update(kwargs)
        return super(RequiredObjectMixin, self).get_context_data(**context)

class ImportView(ExtraContextMixin, RequiredObjectMixin, FormView):
    template_name = "memberships/admin/import_members/form.html"
    form_class = ImportForm

    model = Membership
    pk_url_kwarg = "id"
    context_object_name = "original"
    attribute_name = "membership"

    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)

        form = self.get_form()
        fieldsets = [(None, {'fields': list(form.base_fields)})]
        adminForm = admin.helpers.AdminForm(form, fieldsets, {})
        errors = admin.helpers.AdminErrorList(form, [])

        context.update(
            adminform = adminForm,
            errors = errors
        )
        return context

    def form_valid(self, form):
        # TODO: stick file in s3 and redirect to processing view with filename instead of "tbd"
        url = reverse("admin:process_member_import", kwargs={
            "id": self.membership.id
        })
        return HttpResponseRedirect("%s?%s=%s" % (url, "csv", "tbd"))

class ProcessView(ExtraContextMixin, RequiredObjectMixin, TemplateView):
    template_name = "memberships/admin/import_members/process.html"

    model = Membership
    pk_url_kwarg = "id"
    context_object_name = "original"
    attribute_name = "membership"
