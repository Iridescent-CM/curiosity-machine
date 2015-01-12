# encoding: utf8
from django.db import models, migrations

def set_is_student(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    Profile.objects.filter(is_mentor=False).update(is_student=True)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0012_profile_is_student'),
    ]

    operations = [
        migrations.RunPython(set_is_student, noop)
    ]
