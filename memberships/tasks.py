import django_rq
import os
from django.core.files.storage import default_storage
import tempfile
from django.core.mail import send_mail
from django.conf import settings
from django.core.urlresolvers import reverse
from .reports import MembershipReport
from .models import Membership

def queue_membership_report(object_id, email):
    django_rq.enqueue(run_membership_report, object_id, email)

def run_membership_report(object_id, email):
    membership = Membership.objects.get(pk=object_id)
    report = MembershipReport(membership)
    with tempfile.TemporaryFile(mode='w+') as fp:
        report.write(fp)
        actual_path = default_storage.save(report.path, fp)

    actual_name = os.path.basename(actual_path)
    admin_url = reverse("admin:memberships_membership_get_report", kwargs={
        "object_id": object_id,
        "filename": actual_name
    })
    send_mail(
        'Your report is ready',
        'Your report is ready for download: %s' % settings.SITE_URL + admin_url,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
        html_message = 'Your report is ready for download: <a href="%s">%s</a>' % (settings.SITE_URL + admin_url, actual_name),
    )
