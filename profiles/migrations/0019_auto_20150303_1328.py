# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_auto_20150205_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='consented_at',
            field=models.DateTimeField(blank=True, null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='consent_signature',
            field=models.TextField(blank=True, null=True),
            preserve_default=True,
        ),
    ]
