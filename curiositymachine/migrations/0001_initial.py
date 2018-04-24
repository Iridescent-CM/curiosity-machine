# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-04-17 16:24
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations
from urllib.parse import urlparse

def set_site(apps, schema_editor):
    Site = apps.get_model("sites", "Site")
    if not Site.objects.all().exists():
        Site.objects.create(
            domain=urlparse(settings.SITE_URL).netloc,
            name="Curiosity Machine"
        )

class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(set_site, migrations.RunPython.noop)
    ]