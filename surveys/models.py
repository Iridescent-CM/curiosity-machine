from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from enumfields import Enum, EnumIntegerField
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
        conf = settings.SURVEYS[self.survey_id]
        return "%s?%s=%s" % (conf["link"], settings.SURVEYMONKEY_TOKEN_VAR, self.id)

    def __str__(self):
        return "SurveyResponse: id={}, survey_id={}, user_id={}, status={}".format(
            self.id,
            self.survey_id,
            self.user_id,
            self.status.name
        )

# Middleware pseudocode:
#   for survey in active surveys:
#       if survey applies to user:
#           get or create SurveyResponse for survey link and user
#           if response is not complete:
#               interrupt with link (let's assume only 1 active at a time)

# for survey in settings.SURVEYS if survey.active:
#   if survey.filter(request.user):
#       response = SurveyResponse.objects.get_or_create(user=request.user, survey_id=survey.id)
#       if not response.completed:
#           ..?
