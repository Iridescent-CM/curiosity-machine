from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from enumfields import Enum, EnumIntegerField
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
from . import get_survey
import uuid

class ResponseStatus(Enum):
    UNKNOWN = 0
    COMPLETED = 1
    PARTIAL = 2
    OVERQUOTA = 3
    DISQUALIFIED = 4

class SurveyResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey_id = models.CharField(max_length=30, null=False, blank=False)
    user = models.ForeignKey(get_user_model(), null=False, blank=False)
    status = EnumIntegerField(ResponseStatus, default=ResponseStatus.UNKNOWN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def url(self):
        survey = get_survey(self.survey_id)
        parsed = urlparse(survey.link)
        qs = parse_qs(parsed.query)

        qs[settings.SURVEYMONKEY_TOKEN_VAR] = self.id
        qs['uid'] = self.user_id

        return urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(qs, doseq=True),
            parsed.query
        ))

    def __getattr__(self, name):
        # treat status names like boolean attributes
        try:
            return self.status == ResponseStatus[name.upper()]
        except KeyError:
            pass

        # wrap Survey attributes
        try:
            survey = get_survey(self.survey_id)
            return getattr(survey, name)
        except AttributeError:
            pass

        # okay, there's no attribute by that name
        raise AttributeError("'SurveyResponse' object has no attribute '%s'" % name)

    def __str__(self):
        return "SurveyResponse: id={}, survey_id={}, user_id={}, status={}".format(
            self.id,
            self.survey_id,
            self.user_id,
            self.status.name
        )
