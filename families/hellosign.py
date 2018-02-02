class Signer:
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on(self, signature, from_status, to_status):
        # FIXME: should check signature id against consent form id
        if signature.signed:
            self.user.familyprofile.check_welcome()
