from curiositymachine.middleware import whitelist_regex, whitelisted
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from surveys import get_survey
from .views import prereq_interruption
from surveys.models import *

class CoachPrerequisitesMiddleware:
    """
    Middleware that checks for pre-survey
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (
            request.user.is_authenticated()
            and request.user.extra.is_educator
            and request.user.educatorprofile.is_coach
            and (not request.user.educatorprofile.full_coach_access)
            and not (
                whitelisted(view, 'public', 'maybe_public', 'coach_removal')
                or whitelist_regex.match(request.path.lstrip('/'))
            )
        ):
           return prereq_interruption(request)
