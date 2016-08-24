# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0010_auto_20160819_1526'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='display_name',
            field=models.CharField(help_text='The membership name users will see on the site.', max_length=255),
        ),
    ]
