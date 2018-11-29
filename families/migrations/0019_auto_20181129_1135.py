# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-11-29 19:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations
from hellosign.models import SignatureStatus

def copy_consents(apps, schema_editor):
    Signature = apps.get_model("hellosign", "Signature")
    PermissionSlip = apps.get_model("families", "PermissionSlip")

    for sig in Signature.objects.filter(template_id=settings.AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID, status=SignatureStatus.SIGNED):
        PermissionSlip.objects.create(account=sig.user, signature="HELLOSIGN")

class Migration(migrations.Migration):

    dependencies = [
        ('families', '0018_permissionslip'),
    ]

    operations = [
        migrations.RunPython(copy_consents, migrations.RunPython.noop)
    ]
