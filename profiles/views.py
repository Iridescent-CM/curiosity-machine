from django.contrib.auth.decorators import login_required
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView
from inspect import signature
from .models import UserRole

class ChooseProfileTemplateView(TemplateView):
    template_name = "profiles/choose_profile.html"

choose_profile = ChooseProfileTemplateView.as_view()

class ProfileRedirectView(RedirectView):
    viewname = None

    def get_redirect_url(self, *args, **kwargs):
        role = UserRole(self.request.user.extra.role)
        if role == UserRole.none:
            return reverse("profiles:profiles")
        else:
            return reverse("%ss:%s" % (role.name, self.viewname), args=args, kwargs=kwargs)

home = login_required(ProfileRedirectView.as_view(viewname="home"))
edit_profile = login_required(ProfileRedirectView.as_view(viewname="edit_profile"))

class UserKwargMixin():
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class CreateProfileView(UserKwargMixin, FormView):

    def form_valid(self, form):
        form.save()
        return super().form_valid(form)
