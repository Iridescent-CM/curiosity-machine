from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.conf import settings
import re

whitelist_regex = re.compile('(' + ')|('.join([r for r in settings.WHITELIST_URLS]) + ')')
blacklist_regex = re.compile('(' + ')|('.join([r for r in settings.BLACKLIST_URLS]) + ')')

def whitelisted(view, *listnames):
    """
    True if view belongs to any of the whitelists named in listnames, as marked by the @whitelist() decorator
    """
    whitelists = getattr(view, 'whitelist', [])
    if not whitelists:
        return False
    for name in listnames:
        if name in whitelists:
            return True
    return False

class CanonicalDomainMiddleware:
    """
    Redirects to CANONICAL_DOMAIN from other domains if set
    """
    def process_request(self, request):
        if settings.CANONICAL_DOMAIN and not request.META['HTTP_HOST'] == settings.CANONICAL_DOMAIN:
            return HttpResponseRedirect('http://{}/{}'.format(settings.CANONICAL_DOMAIN, request.get_full_path())) # might as well redirect to http as sslify will then catch requests if appropriate

class LoginRequired(Exception):
    """
    Exception class for views to use to tell LoginRequiredMiddleware to require login
    """
    pass

class LoginRequiredMiddleware:
    """
    Redirects to login if view isn't in 'public' or 'maybe_public' whitelists, or view has raised LoginRequired
    """
    def process_request(self, request):
        if blacklist_regex.match(request.path.lstrip('/')):
            return HttpResponseForbidden()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not (request.user.is_authenticated() or whitelisted(view_func, 'public', 'maybe_public') or whitelist_regex.match(request.path.lstrip('/'))):
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    def process_exception(self, request, exception):
        if isinstance(exception, LoginRequired):        
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

class UnderageStudentSandboxMiddleware:
    """
    Middleware that sandboxes students under 13 away from the rest of the site.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (request.user.is_authenticated()
                and not request.user.is_staff
                and request.user.profile.is_student
                and not request.user.profile.approved):
            if not whitelisted(view, 'public', 'maybe_public', 'underage'):
                return HttpResponseRedirect(reverse('profiles:underage_student'))

class UnapprovedMentorSandboxMiddleware:
    """
    Middleware that sandboxes mentors who have not yet been approved to the training section of the site.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (request.user.is_authenticated()
                and not request.user.is_staff
                and request.user.profile.is_mentor
                and not request.user.profile.approved):
            if not whitelisted(view, 'public', 'maybe_public', 'unapproved_mentors'):
                return HttpResponseRedirect(reverse('profiles:home'))

class LastActiveMiddleware:
    """
    Middleware that updates the last_active_on(or last seen) field of a profile, and maintains shown_intro flag
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.profile.set_active()
        return None

    def process_response(self, request, response):
        if request.user.is_authenticated() and not request.user.profile.shown_intro:
            # assume successful response means they'll be seeing the intro video
            if response.status_code == 200:
                request.user.profile.intro_video_was_played()
        return response
