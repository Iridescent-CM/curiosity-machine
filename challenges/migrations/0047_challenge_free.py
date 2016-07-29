# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0046_remove_challenge_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='free',
            field=models.BooleanField(default=False, help_text='Free challenges are available to users regardless of membership'),
        ),
    ]
