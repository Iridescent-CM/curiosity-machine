# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0010_profile_last_inactive_email_sent_on'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_inactive_email_sent_on',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
