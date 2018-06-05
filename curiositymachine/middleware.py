from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from curiositymachine.exceptions import LoginRequired
import profiles.models
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

class CanonicalDomainMiddleware(MiddlewareMixin):
    """
    Redirects to CANONICAL_DOMAIN from other domains if set
    """
    def process_request(self, request):
        if settings.CANONICAL_DOMAIN and not request.META['HTTP_HOST'] == settings.CANONICAL_DOMAIN:
            return HttpResponseRedirect('http://{}/{}'.format(settings.CANONICAL_DOMAIN, request.get_full_path())) # might as well redirect to http as sslify will then catch requests if appropriate

class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Redirects to login if view isn't in 'public' or 'maybe_public' whitelists, or view has raised LoginRequired
    """
    def process_request(self, request):
        if blacklist_regex.match(request.path.lstrip('/')):
            return HttpResponseForbidden()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not (
            request.user.is_authenticated()
            or whitelisted(view_func, 'public', 'maybe_public')
            or whitelist_regex.match(request.path.lstrip('/'))
        ):
            messages.add_message(
                request,
                messages.INFO,
                "The page you’re trying to view requires being logged in to Curiosity Machine."
            )
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

    def process_exception(self, request, exception):
        if isinstance(exception, LoginRequired):        
            messages.add_message(
                request,
                messages.INFO,
                "The page you’re trying to view requires being logged in to Curiosity Machine."
            )
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.path))

class UnderageStudentSandboxMiddleware(MiddlewareMixin):
    """
    Middleware that sandboxes students under 13 away from the rest of the site.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (request.user.is_authenticated()
                and not request.user.is_staff
                and request.user.extra.is_student
                and not request.user.studentprofile.full_access):
            if (not whitelisted(view, 'public', 'maybe_public', 'underage')
                    and not whitelist_regex.match(request.path.lstrip('/'))):
                return HttpResponseRedirect(reverse('students:underage'))

class UnapprovedMentorSandboxMiddleware(MiddlewareMixin):
    """
    Middleware that sandboxes mentors who have not yet been approved to the training section of the site.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (request.user.is_authenticated()
                and not request.user.is_staff
                and request.user.extra.is_mentor
                and not request.user.mentorprofile.full_access):
            if (not whitelisted(view, 'public', 'maybe_public', 'unapproved_mentors')
                    and not whitelist_regex.match(request.path.lstrip('/'))):
                return HttpResponseRedirect(reverse('profiles:home'))

class UserProxyMiddleware(MiddlewareMixin):
    """
    Middleware that changes request.user to User proxy model
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            profiles.models.User.cast(request.user)
        return None

class LastActiveMiddleware(MiddlewareMixin):
    """
    Middleware that updates the last_active_on(or last seen) field of a profile
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.extra.set_active()
        return None

class FirstLoginMiddleware(MiddlewareMixin):
    """
    Maintains first_login flag used to detect first login
    """
    def process_response(self, request, response):
        if (
            request.user.is_authenticated()
            and request.user.extra.first_login
        ):
            # assume successful response means they'll be seeing the intro video
            if response.status_code == 200:
                request.user.extra.first_login = False
                request.user.extra.save(update_fields=['first_login'])
        return response

class FlushMessagesMiddleware(MiddlewareMixin):
    """
    Middleware that marks messages to be cleared (by iterating them)
    """

    def process_response(self, request, response):
        if response.status_code == 200:
            for message in messages.get_messages(request):
               None
        return response
