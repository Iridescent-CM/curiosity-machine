# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0019_auto_20170120_0805'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='expiration',
            field=models.DateField(null=True, blank=True, help_text='Expired memberships will be automatically made inactive.'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether a membership is considered active. Unselect this when a membership expires instead of deleting it. To restore an inactive membership, enable this and update the expiration date.', verbose_name='Active'),
        ),
    ]
