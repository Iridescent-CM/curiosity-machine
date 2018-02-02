from profiles.models import load_from_role_app
import logging

logger = logging.getLogger(__name__)

class NoopSigner:
    """
    Implement Signer methods and do nothin', used if
    role-specific Signer is not found.
    """
    def __init__(self, *args, **kwargs):
        pass

    def on(self, *args):
        pass

class Updating:
    def __init__(self, signature, new_status, signer=None, *args, **kwargs):
        self.signature = signature
        self.new_status = new_status
        self.signer = signer or self.load_signer(signature.user) or NoopSigner(signature.user)

    def load_signer(self, user):
        signer_class = load_from_role_app(user.extra.role, "hellosign", "Signer")
        if signer_class:
            return signer_class(user)
        return None

    def run(self):
        """
        Updates a Signature with a new status and gives a Signer
        a chance to do role-specific actions based on the state transition.
        """
        signature = self.signature
        new_status = self.new_status
        signer = self.signer

        status = signature.status

        if signature.signed:
            logger.warn("Updating a %s signature to %s" % (status, new_status))

        signature.status = new_status
        signature.save(update_fields=['status'])

        signer.on(signature, status, new_status)

        return signature

