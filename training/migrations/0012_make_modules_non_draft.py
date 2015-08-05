# encoding: utf8
from django.db import models, migrations


def make_non_draft(apps, schema_editor):
    Module = apps.get_model("training", "Module")
    Module.objects.all().update(draft=False)

def noop(apps, schema_editor):
    return

class Migration(migrations.Migration):

    dependencies = [
        ('training', '0011_module_draft'),
    ]

    operations = [
        migrations.RunPython(make_non_draft, noop)
    ]
