from django.contrib.auth.decorators import login_required
from django.http import Http404
import password_reset.views
from smtplib import SMTPRecipientsRefused

# TODO: handle staff views in new app?
from . import staff

@login_required
def dispatch(request, action, *args, **kwargs):
    if request.user.is_staff:
        module = staff
    else:
        raise Http404()

    fn = getattr(module, action, None)
    if fn:
        return fn(request, *args, **kwargs)
    else:
        raise Http404()

# TODO: move to allauth password recovery
### password recovery

class Recover(password_reset.views.Recover):
    search_fields = ['username'] # search only on username, not on email. this is important because email is not a unique field in this app!

    def send_notification(self):
        try:
            super().send_notification()
        except SMTPRecipientsRefused as ex:
            # swallow (but log) SMTPRecipientsRefused errors
            logger.warning("Password reset recipients refused", exc_info=ex)
        except:
            raise

recover = Recover.as_view()

################# New stuff
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse
from django.views.generic.base import TemplateView, RedirectView
from django.views.generic.edit import FormView
from inspect import signature
from ..models import UserRole

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
