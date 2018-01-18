from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from enumfields import Enum, EnumIntegerField
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

    @property
    def completed(self):
        return self.status == ResponseStatus.COMPLETED

    @property
    def url(self):
        survey = get_survey(self.survey_id)
        return "%s?%s=%s" % (survey.link, settings.SURVEYMONKEY_TOKEN_VAR, self.id)

    @property
    def title(self):
        survey = get_survey(self.survey_id)
        return survey.title

    def __str__(self):
        return "SurveyResponse: id={}, survey_id={}, user_id={}, status={}".format(
            self.id,
            self.survey_id,
            self.user_id,
            self.status.name
        )
