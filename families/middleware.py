from curiositymachine.middleware import whitelist_regex, whitelisted
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from surveys import get_survey
from curiositymachine.presenters import LearningSet
from .views import prereq_interruption, postsurvey_interruption, sign_slip

class SignUpPrerequisitesMiddleware(MiddlewareMixin):
    """
    Middleware that checks for pre-survey and permission slips.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        user = request.user
        if (
            user.is_authenticated()
            and user.extra.is_family
            and not (
                whitelisted(view, 'public', 'maybe_public', 'unapproved_family')
                or whitelist_regex.match(request.path.lstrip('/'))
            )
            and not user.familyprofile.full_access
        ):
            if not user.familyprofile.permission_slip_signed:
                return sign_slip(request)

            return prereq_interruption(request)

