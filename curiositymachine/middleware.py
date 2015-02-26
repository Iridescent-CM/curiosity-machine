from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings

class CanonicalDomainMiddleware:
    """
    Redirects to CANONICAL_DOMAIN from other domains if set
    """
    def process_request(self, request):
        if settings.CANONICAL_DOMAIN and not request.META['HTTP_HOST'] == settings.CANONICAL_DOMAIN:
            return HttpResponseRedirect('http://{}/{}'.format(settings.CANONICAL_DOMAIN, request.get_full_path())) # might as well redirect to http as sslify will then catch requests if appropriate

class UnderageStudentSandboxMiddleware:
    """
    Middleware that sandboxes students under 13 away from the rest of the site.
    """
    def process_request(self, request):
        if (request.user.is_authenticated()
                and not request.user.is_staff
                and request.user.profile.is_student
                and not request.user.profile.approved):
            if request.path_info not in ['/logout', '/logout/', reverse('profiles:underage_student'), reverse('profiles:consent_form')]:
                return HttpResponseRedirect(reverse('profiles:underage_student'))

class UnapprovedMentorSandboxMiddleware:
    """
    Middleware that sandboxes mentors who have not yet been approved to the training section of the site.
    """
    def process_request(self, request):
        if (request.user.is_authenticated()
                and not request.user.is_staff
                and request.user.profile.is_mentor
                and not request.user.profile.approved):
            if (request.path_info not in ['/logout', '/logout/', reverse('profiles:home'), reverse('profiles:profile_edit')]
                    and not request.path_info.startswith('/training')):
                return HttpResponseRedirect(reverse('profiles:home'))

class LastActiveMiddleware:
    """
    Middleware that updates the last_active_on(or last seen) field of a profile
    """
    def process_request(self, request):
        if request.user.is_authenticated():
            request.user.profile.set_active()
        return None
