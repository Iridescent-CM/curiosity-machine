# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_profile_last_active_on'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_inactive_email_sent_on',
            field=models.DateTimeField(null=True, default=None),
            preserve_default=True,
        ),
    ]
