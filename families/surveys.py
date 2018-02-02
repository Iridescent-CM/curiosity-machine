from surveys.models import ResponseStatus

class Responder:
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on(self, survey_response, from_status, to_status):
        if to_status == ResponseStatus.COMPLETED:
            self.user.familyprofile.check_welcome()
