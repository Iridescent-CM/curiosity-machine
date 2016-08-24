# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0008_memberimport'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='display_name',
            field=models.CharField(max_length=255, help_text='The membership name users will see on the site.', null=True),
        ),
    ]
