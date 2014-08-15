# encoding: utf8
from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0008_remove_profile_nickname'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_active_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=True,
        ),
    ]
