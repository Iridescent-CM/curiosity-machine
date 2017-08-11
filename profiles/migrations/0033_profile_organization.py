# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0032_impactsurvey'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='organization',
            field=models.CharField(help_text='This is an educator field.', max_length=50, blank=True, null=True),
        ),
    ]
