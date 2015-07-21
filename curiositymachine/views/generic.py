from django.http import HttpResponseRedirect, Http404
from django.views.generic.edit import DeleteView, CreateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_text
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

class UserJoinView(CreateView):
    logged_in_redirect = None
    success_message = None
    template_names = None

    def get_logged_in_redirect(self):
        return self.logged_in_redirect

    def get_success_message(self):
        return self.success_message

    def get_template_names(self):
        prefix = self.get_prefix()
        templates = ["profiles/{}/join.html".format(prefix)]
        if self.source:
            templates.insert(0, "profiles/sources/{}/{}/join.html".format(self.source, prefix))
        return templates

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponseRedirect(self.get_logged_in_redirect())
        else:
            return super(UserJoinView, self).get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.source = None
        if 'source' in kwargs:
            self.source = kwargs['source']
        return super(UserJoinView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserJoinView, self).get_context_data(**kwargs)
        context['source'] = self.source
        context['action'] = self.request.path
        return context

    def get_initial(self):
        initial = super(UserJoinView, self).get_initial()
        if self.source:
            initial['source'] = self.source
        return initial

    def get_form_kwargs(self):
        kwargs = super(UserJoinView, self).get_form_kwargs()
        if 'data' in kwargs:
            data = kwargs['data']
            request = self.request

            source_field = 'source'
            if self.get_prefix():
                source_field = self.get_prefix() + '-' + source_field

            if self.source:
                if self.source != data.get(source_field):
                    logger.warn("Form submitted to {} with source={}; setting source from url".format(request.path, data.get(source_field)))
                    data[source_field] = self.source
            else:
                if data.get(source_field):
                    logger.warn("Form submitted to {} with source={}; removing source".format(request.path, data.get(source_field)))
                    del data[source_field]

            kwargs['data'] = data
        return kwargs

    def form_valid(self, form):
        request = self.request
        self.object = form.save()
        user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        auth.login(request, user)
        user.profile.deliver_welcome_email()
        if self.get_success_message():
            messages.success(request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())
        