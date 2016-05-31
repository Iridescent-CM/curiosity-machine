from django.views.generic.base import TemplateView
from django.shortcuts import get_object_or_404
from memberships.models import Membership

class ImportView(TemplateView):
    template_name = "memberships/admin/import_members/form.html"

    def dispatch(self, request, *args, **kwargs):
        self.membership = get_object_or_404(Membership, id=kwargs.get('id'))
        return super(ImportView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ImportView, self).get_context_data(**kwargs)
        context['original'] = self.membership
        return context
