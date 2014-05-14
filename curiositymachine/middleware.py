from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

class UnderageStudentSandboxMiddleware:
    """
    Middleware that sandboxes students under 13 away from the rest of the site.
    """
    def process_request(self, request):
        if request.user.is_authenticated() and request.user.profile.age < 13 and not request.user.profile.approved:
            # if under 13 and not yet approved
            if request.path_info not in ['/logout', '/logout/', reverse('profiles:underage_student')]:
                return HttpResponseRedirect(reverse('profiles:underage_student'))
