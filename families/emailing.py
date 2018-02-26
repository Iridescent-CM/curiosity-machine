from cmemails import send

class Emailing:
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def send_stage_completion_email(self, stage):
        if stage.number == 1:
            send(template_name='family-account-completed-stage-1', to=self.user, merge_vars={
                "username": self.user.username,
            })

