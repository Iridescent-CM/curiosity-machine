# encoding: utf8
from django.db import models, migrations
from django.db.models import Q
from django.db.utils import DataError
from profiles.models import UserRole


def set_role(apps, schema_editor):
    Profiles = apps.get_model("profiles", "Profile")
    usernames = Profiles.objects.filter(
        Q(is_student=True, is_mentor=True)
        | Q(is_student=True, is_educator=True)
        | Q(is_student=True, is_parent=True)
        | Q(is_mentor=True, is_educator=True)
        | Q(is_mentor=True, is_parent=True)
        | Q(is_educator=True, is_parent=True)
    ).values_list('user__username', flat=True)
    if len(usernames) > 0:
        raise DataError("Cannot migrate %d profiles with multiple role flags set: %s" % (len(usernames), ", ".join(usernames)))

    Profiles.objects.filter(is_student=True, role=UserRole.none.value).update(role=UserRole.student.value)
    Profiles.objects.filter(is_mentor=True, role=UserRole.none.value).update(role=UserRole.mentor.value)
    Profiles.objects.filter(is_educator=True, role=UserRole.none.value).update(role=UserRole.educator.value)
    Profiles.objects.filter(is_parent=True, role=UserRole.none.value).update(role=UserRole.parent.value)

def set_flags(apps, schema_editor):
    Profiles = apps.get_model("profiles", "Profile")

    Profiles.objects.filter(role=UserRole.student.value).update(is_student=True)
    Profiles.objects.filter(role=UserRole.mentor.value).update(is_mentor=True)
    Profiles.objects.filter(role=UserRole.educator.value).update(is_educator=True)
    Profiles.objects.filter(role=UserRole.parent.value).update(is_parent=True)

class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0028_profile_role'),
    ]

    operations = [
        migrations.RunPython(set_role, set_flags)
    ]
