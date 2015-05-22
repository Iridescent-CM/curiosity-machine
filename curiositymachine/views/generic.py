from django.http import HttpResponseRedirect, Http404
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text

class ToggleView(SingleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.toggle(obj)
        return HttpResponseRedirect(force_text(self.success_url))

    def toggle(self, obj):
        raise ImproperlyConfigured("You must override toggle")