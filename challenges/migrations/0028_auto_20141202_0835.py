# encoding: utf8
from django.db import models, migrations


def make_non_draft(apps, schema_editor):
    Challenge = apps.get_model("challenges", "Challenge")
    Challenge.objects.all().update(draft=False)

def noop(apps, schema_editor):
    return

class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_challenge_draft'),
    ]

    operations = [
        migrations.RunPython(make_non_draft, noop)
    ]
