from django.http import HttpResponse
import csv
import tempfile
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.exceptions import PermissionDenied

User = get_user_model()

def export_users(request):
    if not request.user.has_perms(['auth.change_user', 'cmcomments.change_comment', 'challenges.change_progress']):
        raise PermissionDenied
    return generate_export_users()    


def generate_export_users():
    with tempfile.TemporaryFile(mode='w+') as fp:
        writer = csv.writer(fp)
        writer.writerow(["User Id", "First name", "Last Name", "Location", "Role", "Approved","Date Joined y-m-d"])

        users = User.objects.all()
        for user in users:
            writer.writerow([
                user.id, 
                user.first_name,
                user.last_name,
                user.profile.city,
                user.extra.user_type,
                str(True) if user.is_superuser else str(user.extra.approved),
                user.date_joined.strftime('%Y-%m-%d')
            ])

        fp.seek(0)
        response = HttpResponse(fp, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=cm-users-%s.csv' % (now().strftime('%Y-%m-%d'))
        return response