from profiles.models import load_from_role_app
from .models import ResponseStatus
import logging

logger = logging.getLogger(__name__)

class NoopResponder:
    """
    Implement Responder methods and do nothin', used if
    role-specific Responder is not found.
    """
    def __init__(self, *args, **kwargs):
        pass

    def on(self, from_status, to_status):
        pass

class Updating:
    def __init__(self, survey_response, new_status, responder=None, *args, **kwargs):
        self.survey_response = survey_response
        self.new_status = new_status
        self.responder = responder or self.load_responder(survey_response.user) or NoopResponder(survey_response.user)

    def load_responder(self, user):
        responder_class = load_from_role_app(user.extra.role, "surveys", "Responder")
        if responder_class:
            return responder_class(user)
        return None

    def run(self):
        """
        Updates a SurveyResponse with a new status and gives a Responder
        a chance to do role-specific actions based on the state transition.
        """
        survey_response = self.survey_response
        new_status = self.new_status
        responder = self.responder

        status = survey_response.status

        if survey_response.completed:
            logger.warn("Updating a %s survey to %s" % (survey_response.status, new_status))

        survey_response.status = new_status 
        survey_response.save(update_fields=['status'])

        responder.on(status, new_status)

        return survey_response

