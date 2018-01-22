from django.conf import settings

class Survey:
    def __init__(self, id, *args, **kwargs):
        self.id = id

    def __getattr__(self, name):
        return getattr(settings, "SURVEY_%s_%s" % (self.id, name.upper()))

    def response(self, user):
        from .models import SurveyResponse
        response, created = SurveyResponse.objects.get_or_create(user=user, survey_id=self.id)
        return response

def get_survey(id):
    return Survey(id)
