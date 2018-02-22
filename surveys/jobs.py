from django.conf import settings
from .api import Surveymonkey
from .models import *
from .updating import Updating
import logging

logger = logging.getLogger(__name__)
api = Surveymonkey()

def update_status(survey_id, response_id):
    token_var = settings.SURVEYMONKEY_TOKEN_VAR

    res = api.get("surveys/%s/responses/%s" % (survey_id, response_id))
    res.raise_for_status()

    data = res.json()
    try:
        custom_vars = data['custom_variables']
        new_status = data['response_status']
    except KeyError:
        logger.error("API response did not contain expected fields: %s" % data)
        raise

    token = custom_vars.get(token_var, None)
    if token:
        sr = SurveyResponse.objects.filter(id=token).first()
        if sr:
            logger.info("SurveyResponse %s=%s moving to %s", token_var, token, new_status)
            status = ResponseStatus[new_status.upper()]
            Updating(sr, status).run()
        else:
            logger.info("SurveyResponse not found for id=%s; assuming it's in another environment" % token)
    else:
        logger.info(
            "No %s custom variable for survey %s response %s; assuming survey taken by non-user" % (token_var, survey_id, response_id)
        )

