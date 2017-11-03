from django.contrib.auth.decorators import login_required
from django.http import Http404
import password_reset.views
import password_reset.forms
from smtplib import SMTPRecipientsRefused
import logging

from . import student
from . import mentor
from . import educator
from . import staff
from . import parent

logger = logging.getLogger(__name__)

@login_required
def dispatch(request, action, *args, **kwargs):
    if request.user.profile.is_mentor:
        module = mentor
    elif request.user.profile.is_student:
        module = student
    elif request.user.profile.is_educator:
        module = educator
    elif request.user.profile.is_parent:
        module = parent
    elif request.user.is_staff:
        module = staff
    else:
        raise Http404()

    fn = getattr(module, action, None)
    if fn:
        return fn(request, *args, **kwargs)
    else:
        raise Http404()

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
from django.urls import reverse
from django.views.generic.base import TemplateView, RedirectView
from ..models import UserRole

class ChooseProfileTemplateView(TemplateView):
    template_name = "profiles/choose_profile.html"

choose_profile = ChooseProfileTemplateView.as_view()

class HomeRedirectView(RedirectView):

    def get_redirect_url(self, *args, **kwargs):
        role = UserRole(self.request.user.profile.role)
        if role == UserRole.none:
            return reverse("profiles:profiles")
        else:
            return reverse("%ss:home" % role.name, args=args, kwargs=kwargs)

home = HomeRedirectView.as_view()
