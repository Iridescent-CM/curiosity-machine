from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import reverse
from django.conf import settings
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from django.utils.encoding import escape_uri_path
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

class LoginRequiredMiddleware(MiddlewareMixin):
    """
    Redirects to login if view isn't in 'public' or 'maybe_public' whitelists, or view has raised LoginRequired
    """
    def process_request(self, request):
        if blacklist_regex.match(request.path.lstrip('/')):
            return HttpResponseForbidden()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not (
            request.user.is_authenticated
            or whitelisted(view_func, 'public', 'maybe_public')
            or whitelist_regex.match(request.path.lstrip('/'))
        ):
            messages.add_message(
                request,
                messages.INFO,
                "The page you’re trying to view requires being logged in to Curiosity Machine."
            )
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), escape_uri_path(request.get_full_path())))

    def process_exception(self, request, exception):
        if isinstance(exception, LoginRequired):        
            messages.add_message(
                request,
                messages.INFO,
                "The page you’re trying to view requires being logged in to Curiosity Machine."
            )
            return HttpResponseRedirect('%s?next=%s' % (reverse('login'), request.get_full_path()))

class UnapprovedStudentSandboxMiddleware(MiddlewareMixin):
    """
    Middleware that sandboxes unapproved students
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (request.user.is_authenticated
                and not request.user.is_staff
                and request.user.extra.is_student
                and not request.user.studentprofile.full_access):
            if (not whitelisted(view, 'public', 'maybe_public', 'unapproved_students')
                    and not whitelist_regex.match(request.path.lstrip('/'))):
                return HttpResponseRedirect(reverse('students:unapproved'))

class UserProxyMiddleware(MiddlewareMixin):
    """
    Middleware that changes request.user to User proxy model
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            profiles.models.User.cast(request.user)
        return None

class LastActiveMiddleware(MiddlewareMixin):
    """
    Middleware that updates the last_active_on(or last seen) field of a profile
    """
    def process_request(self, request):
        if request.user.is_authenticated:
            request.user.extra.set_active()
        return None

class FirstLoginMiddleware(MiddlewareMixin):
    """
    Maintains first_login flag used to detect first login
    """
    def process_response(self, request, response):
        if (
            request.user.is_authenticated
            and request.user.extra.first_login
        ):
            # assume successful response means they'll be seeing the intro video
            if response.status_code == 200:
                request.user.extra.first_login = False
                request.user.extra.save(update_fields=['first_login'])
        return response
