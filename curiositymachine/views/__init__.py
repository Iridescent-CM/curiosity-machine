from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.conf import settings

def root(request):
    # redirect to home if logged in unless you are a student with no challenges
    if request.user.is_authenticated():
        if (not request.user.profile.is_student or request.user.progresses.exists()):
            return HttpResponseRedirect(reverse('profiles:home'))
        else:
            return HttpResponseRedirect(reverse('challenges:challenges'))
    else:
        return render(request, "curiositymachine/index.html")

def health_check(request):
    return HttpResponse('OK')

def csrf_failure_handler(request, reason=""):
	from django.middleware.csrf import REASON_NO_REFERER, REASON_NO_CSRF_COOKIE
	ctx = {
        'title': _("Forbidden"),
        'main': _("Session Expired"),
        'contact_email': settings.CONTACT_EMAIL if settings.CONTACT_EMAIL else "contactcm@mailinator.com",
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