from django.conf import settings

class Survey:

    defaults = {
        "ACTIVE": False,
        "MESSAGE": ""
    }

    def __init__(self, id, *args, **kwargs):
        self.id = id

    def __getattr__(self, name):
        name = name.upper()
        if name in self.defaults:
            return getattr(settings, "SURVEY_%s_%s" % (self.id, name), self.defaults[name])
        return getattr(settings, "SURVEY_%s_%s" % (self.id, name))

    def response(self, user):
        from .models import SurveyResponse
        response, created = SurveyResponse.objects.get_or_create(user=user, survey_id=self.id)
        return response

def get_survey(id):
    return Survey(id)
