from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class UnderageStudentSandboxMiddleware:
    """
    Middleware that sandboxes students under 13 away from the rest of the site.
    """
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_staff and not request.user.profile.is_mentor and not request.user.profile.approved:
            # if not yet approved
            if request.path_info not in ['/logout', '/logout/', reverse('profiles:underage_student')]:
                return HttpResponseRedirect(reverse('profiles:underage_student'))

class UnapprovedMentorSandboxMiddleware:
    """
    Middleware that sandboxes mentors who have not yet been approved to the training section of the site.
    """
    def process_request(self, request):
        if request.user.is_authenticated() and not request.user.is_staff and request.user.profile.is_mentor and not request.user.profile.approved:
            if request.path_info not in ['/logout', '/logout/', reverse('profiles:home'), reverse('profiles:profile_edit')] and not request.path_info.startswith('/training'):
                return HttpResponseRedirect(reverse('profiles:home'))
