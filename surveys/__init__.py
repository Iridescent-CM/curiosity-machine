from django.conf import settings

class Survey:
    def __init__(self, id, *args, **kwargs):
        self.id = id

    def __getattr__(self, name):
        return getattr(settings, "SURVEY_%s_%s" % (self.id, name.upper()))

def get_survey(id):
    return Survey(id)
