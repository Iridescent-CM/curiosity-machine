from surveys.models import ResponseStatus
from . import welcoming

class Responder:
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on(self, from_status, to_status):
        if to_status == ResponseStatus.COMPLETED:
            welcoming.check(self.user)
