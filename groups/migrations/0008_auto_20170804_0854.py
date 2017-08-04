# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0007_auto_20160506_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='group',
            name='invited_users',
        ),
        migrations.RemoveField(
            model_name='group',
            name='member_users',
        ),
        migrations.AlterUniqueTogether(
            name='invitation',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='group',
        ),
        migrations.RemoveField(
            model_name='invitation',
            name='user',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='group',
        ),
        migrations.RemoveField(
            model_name='membership',
            name='user',
        ),
        migrations.DeleteModel(
            name='Group',
        ),
        migrations.DeleteModel(
            name='Invitation',
        ),
        migrations.DeleteModel(
            name='Membership',
        ),
    ]
