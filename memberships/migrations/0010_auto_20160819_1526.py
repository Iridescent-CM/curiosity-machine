# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F

def copy_name(apps, schema_editor):
    Membership = apps.get_model("memberships", "Membership")
    Membership.objects.filter(display_name__isnull=True).all().update(display_name=F('name'))

def noop(apps, schema_editor):
    return

class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0009_membership_display_name'),
    ]

    operations = [
        migrations.RunPython(copy_name, noop)
    ]
