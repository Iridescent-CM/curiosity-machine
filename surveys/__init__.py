from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

class Survey:

    defaults = {
        "ACTIVE": False,
        "MESSAGE": ""
    }

    def __init__(self, id, *args, **kwargs):
        self.id = id
        if not self.id:
            raise ImproperlyConfigured('Can not instantiate Survey without a valid id')
        try:
            self.link
        except AttributeError:
            raise ImproperlyConfigured('SURVEY_%s_LINK must be properly configured' % self.id)

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
