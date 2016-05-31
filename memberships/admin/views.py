from django.views.generic.base import TemplateView

class ImportView(TemplateView):
    template_name = "memberships/admin/import_members/form.html"
