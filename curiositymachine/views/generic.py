from curiositymachine.context_processors.google_analytics import add_event
from django.http import HttpResponseRedirect, Http404
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text
from django.utils.http import is_safe_url
from django.contrib import auth, messages
import logging

logger = logging.getLogger(__name__)

class ToggleView(SingleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.toggle(obj)
        return HttpResponseRedirect(force_text(self.success_url))

    def toggle(self, obj):
        raise ImproperlyConfigured("You must override toggle")

class SoftDeleteView(DeleteView):

    def get_deletion_field(self):
        if self.deletion_field:
            return self.deletion_field
        else:
            raise ImproperlyConfigured("No soft deletion indicator fieldname given. Provide a deletion_field.")

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        deletion_field = self.get_deletion_field()
        setattr(self.object, deletion_field, True)
        self.object.save(update_fields=[deletion_field])
        return HttpResponseRedirect(success_url)