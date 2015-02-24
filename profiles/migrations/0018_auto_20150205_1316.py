# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0017_profile_is_educator'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='shown_intro',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
