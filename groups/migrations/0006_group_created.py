# encoding: utf8
from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0005_group_invited_users'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='created',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
