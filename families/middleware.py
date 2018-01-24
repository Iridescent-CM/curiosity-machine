from curiositymachine.middleware import whitelist_regex, whitelisted
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from hellosign.models import ConsentTemplate
from surveys import get_survey
from .views import prereq_interruption

class SignUpPrerequisitesMiddleware:
    """
    Middleware that checks for pre-survey and permission slips.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (
            request.user.is_authenticated()
            and request.user.extra.is_family
            and not (
                whitelisted(view, 'public', 'maybe_public')
                or whitelist_regex.match(request.path.lstrip('/'))
            )
        ):
            presurvey = get_survey(settings.AICHALLENGE_FAMILY_PRE_SURVEY_ID)
            if presurvey.active:
                response = presurvey.response(request.user)
                if not response.completed:
                    return prereq_interruption(request)

            consent = ConsentTemplate(settings.AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID)
            if consent.active:
                signature = consent.signature(request.user)
                if not signature.signed:
                    return prereq_interruption(request)

        return None

