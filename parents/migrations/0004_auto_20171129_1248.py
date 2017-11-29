# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-11-29 20:48
from __future__ import unicode_literals

from django.db import migrations

def copy(apps, schema_editor):
    ProfileParentConnection = apps.get_model("profiles", "ParentConnection")
    ParentConnection = apps.get_model("parents", "ParentConnection")
    for connection in ProfileParentConnection.objects.all():
        ParentConnection.objects.create(
            parent_profile=connection.parent_profile.user.parentprofile,
            child_profile=connection.child_profile.user.studentprofile,
            active=connection.active,
            removed=connection.removed,
            retries=connection.retries
        )

class Migration(migrations.Migration):

    dependencies = [
        ('parents', '0003_auto_20171107_1740'),
    ]

    operations = [
        migrations.RunPython(copy)
    ]
