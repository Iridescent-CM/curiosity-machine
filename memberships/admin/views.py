from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404
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
        context.update(
            self.extra_context,
            original = self.membership
        )
        return context
