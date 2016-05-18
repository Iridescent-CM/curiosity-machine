# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0006_group_created'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='invited_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='cm_group_invites', through='groups.Invitation'),
        ),
        migrations.AlterField(
            model_name='group',
            name='member_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='cm_groups', through='groups.Membership'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='group',
            field=models.ForeignKey(to='groups.Group', related_name='group_invitations'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='user_invitations'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='group',
            field=models.ForeignKey(to='groups.Group', related_name='memberships'),
        ),
        migrations.AlterField(
            model_name='membership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='memberships'),
        ),
    ]
