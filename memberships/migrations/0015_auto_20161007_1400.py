# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0014_membership_units'),
    ]

    operations = [
        migrations.RenameField(
            model_name='membership',
            old_name='units',
            new_name='extra_units',
        ),
    ]
