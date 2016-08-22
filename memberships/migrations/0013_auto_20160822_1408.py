# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0012_auto_20160822_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='display_name',
            field=models.CharField(help_text='The membership name users will see on the site (max 26 characters).', max_length=26),
        ),
    ]
