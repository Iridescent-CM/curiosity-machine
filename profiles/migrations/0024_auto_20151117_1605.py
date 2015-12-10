# encoding: utf8
from django.db import models, migrations

def set_source(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    Profile.objects.filter(source__isnull=True).update(source="")

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0023_profile_source'),
    ]

    operations = [
        migrations.RunPython(set_source, noop)
    ]
