from .api import HelloSign
from .models import Signature
import django_rq

def request_signature(signature_id):
    django_rq.enqueue(_request_signature_job, signature_id)

def _request_signature_job(signature_id):
    api = HelloSign()
    signature = Signature.objects.get(id=signature_id)
    api.request_signature(signature)

def update_email(signature_id):
    django_rq.enqueue(_update_email_job, signature_id)

def _update_email_job(signature_id):
    api = HelloSign()
    signature = Signature.objects.get(id=signature_id)
    api.update_email(signature)
