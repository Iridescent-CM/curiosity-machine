class Signer:
    def __init__(self, user, *args, **kwargs):
        self.user = user

    def on(self, signature, from_status, to_status):
        # This lazily assumes that the signature is on the parent consent form, which is the only one sent out currently.
        if signature.signed:
            self.user.studentprofile.full_access = True
            self.user.studentprofile.save()
