# encoding: utf8
from django.db import models, migrations

def copy_themes(apps, schema_editor):
    Challenge = apps.get_model("challenges", "Challenge")
    for challenge in Challenge.objects.filter(theme__isnull=False).select_related('theme'):
        challenge.themes.add(challenge.theme)
        challenge.save()

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0033_challenge_themes'),
    ]

    operations = [
        migrations.RunPython(copy_themes, noop)
    ]
