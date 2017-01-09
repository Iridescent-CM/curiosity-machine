# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0017_membership_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=255)),
                ('membership', models.ForeignKey(to='memberships.Membership')),
            ],
        ),
        migrations.AddField(
            model_name='member',
            name='groups',
            field=models.ManyToManyField(blank=True, to='memberships.Group'),
        ),
        migrations.AlterUniqueTogether(
            name='group',
            unique_together=set([('membership', 'name')]),
        ),
    ]
