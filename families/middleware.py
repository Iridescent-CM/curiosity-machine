from curiositymachine.middleware import whitelist_regex, whitelisted
from django.conf import settings
from django.http import HttpResponseRedirect, HttpResponse
from surveys import get_survey
from .aichallenge import Stage
from .views import prereq_interruption, postsurvey_interruption

class SignUpPrerequisitesMiddleware:
    """
    Middleware that checks for pre-survey and permission slips.
    """
    def process_view(self, request, view, view_args, view_kwargs):
        if (
            request.user.is_authenticated()
            and request.user.extra.is_family
            and not request.user.familyprofile.full_access
            and not (
                whitelisted(view, 'public', 'maybe_public', 'unapproved_family')
                or whitelist_regex.match(request.path.lstrip('/'))
            )
        ):
            return prereq_interruption(request)

class PostSurveyMiddleware:
    """
    Middleware that interrupts at the appropriate point to prompt users to take post-survey.
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
            stage1 = Stage.from_config(1, user=request.user)
            stage2 = Stage.from_config(2, user=request.user)
            if stage1.stats["completed"] + stage2.stats["completed"] >= 5:
                post_survey = get_survey(settings.AICHALLENGE_FAMILY_POST_SURVEY_ID)
                if post_survey.active:
                    response = post_survey.response(request.user)
                    if not response.completed:
                        return postsurvey_interruption(request)
