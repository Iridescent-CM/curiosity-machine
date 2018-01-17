from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from surveys.models import *

class SignUpPrerequisitesMiddleware:
    """
    Middleware that checks for pre-survey and permission slips.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (
            request.user.is_authenticated()
            and request.user.extra.is_family
        ):
            for survey_id, survey in settings.SURVEYS.items():
                if survey["active"] and survey["filter"](request.user):
                    response, created = SurveyResponse.objects.get_or_create(user=request.user, survey_id=survey_id)
                    if not response.completed:
                        pass # redirect to interruption?
        return None

