# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.db.models import F
from django.db.models.functions import Length, Substr


def truncate_display_names(apps, schema_editor):
    Membership = apps.get_model("memberships", "Membership")
    (Membership.objects
        .annotate(display_name_length=Length('display_name'))
        .filter(display_name_length__gt=26)
        .update(display_name=Substr('display_name', 1, 26)))

def noop(apps, schema_editor):
    return

class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0011_auto_20160819_1537'),
    ]

    operations = [
        migrations.RunPython(truncate_display_names, noop)
    ]
