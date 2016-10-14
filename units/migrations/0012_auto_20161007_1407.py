# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def set_listed(apps, schema_editor):
    Unit = apps.get_model("units", "Unit")
    Unit.objects.filter(draft=False).all().update(listed=True)

def set_draft(apps, schema_editor):
    Unit = apps.get_model("units", "Unit")
    Unit.objects.filter(listed=True).all().update(draft=False)

class Migration(migrations.Migration):

    dependencies = [
        ('units', '0011_unit_listed'),
    ]

    operations = [
        migrations.RunPython(set_listed, set_draft)
    ]
