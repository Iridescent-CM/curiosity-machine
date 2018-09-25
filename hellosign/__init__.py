from .signrequest import send_student_consent_form as _send_student_consent_form
import django_rq


default_app_config = 'hellosign.apps.HellosignConfig'


def send_student_consent_form(sender):
    django_rq.enqueue(_send_student_consent_form, sender)
