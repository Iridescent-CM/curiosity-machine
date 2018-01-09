from allauth.account.views import SignupView
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404
from django.utils.translation import ugettext as _
from django.conf import settings
from django.views.decorators.http import require_http_methods
from memberships.models import Member, Membership
import json
import rollbar

def root(request):
    # redirect to home if logged in unless you are a student with no challenges
    if request.user.is_authenticated():
        if (not request.user.extra.is_student or request.user.progresses.exists()):
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            return HttpResponseRedirect(reverse('challenges:challenges'))
    else:
        return render(request, "curiositymachine/index.html")

def health_check(request):
    return HttpResponse('OK')

@require_http_methods(["PUT"])
def log(request):
    data = json.loads(request.body.decode('utf-8')) if request.body else {}
    rollbar.report_message(
        data.get("message", "PUT to log endpoint"),
        data.get("level", "info"),
        request,
        extra_data=data
    )
    return HttpResponse("OK")

def csrf_failure_handler(request, reason=""):
	from django.middleware.csrf import REASON_NO_REFERER, REASON_NO_CSRF_COOKIE
	ctx = {
        'title': _("Forbidden"),
        'main': _("Session Expired"),
        'contact_email': settings.CONTACT_EMAIL,
        'reason': reason,
        'no_referer': reason == REASON_NO_REFERER,
        'no_referer1': _(
            "You are seeing this message because this HTTPS site requires a "
            "'Referer header' to be sent by your Web browser, but none was "
            "sent. This header is required for security reasons, to ensure "
            "that your browser is not being hijacked by third parties."),
        'no_referer2': _(
            "If you have configured your browser to disable 'Referer' headers, "
            "please re-enable them, at least for this site, or for HTTPS "
            "connections, or for 'same-origin' requests."),
        'no_cookie': reason == REASON_NO_CSRF_COOKIE,
        'no_cookie1': _(
            "You are seeing this message because this site requires a CSRF "
            "cookie when submitting forms. This cookie is required for "
            "security reasons, to ensure that your browser is not being "
            "hijacked by third parties."),
        'no_cookie2': _(
            "If you have configured your browser to disable cookies, please "
            "re-enable them, at least for this site, or for 'same-origin' "
            "requests."),
        'DEBUG': settings.DEBUG,
        'more': _("More information is available with DEBUG=True."),
    }
	return render(request, 'error/csrf.html', ctx)

class SourceSignupView(SignupView):

    def get(self, request, *args, **kwargs):
        self.source = kwargs.get('source', None)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.source = request.POST.get('source', kwargs.get('source', None))
        return super().post(request, *args, **kwargs)

    def get_template_names(self):
        return ["account/%s/signup.html" % self.source, self.template_name]

    def get_initial(self):
        initial = super().get_initial()
        initial['source'] = self.source
        return initial

signup_with_source = SourceSignupView.as_view()

class MembershipSignupView(SignupView):

    def dispatch(self, request, *args, **kwargs):
        slug = kwargs.get('slug', None)
        if not slug:
            raise Http404
        self.membership = get_object_or_404(Membership, slug=slug)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(membership=self.membership)

    def form_valid(self, form):
        res = super().form_valid(form)
        member = Member(user=self.user, membership=self.membership)
        member.save()
        return res

signup_to_membership = MembershipSignupView.as_view()