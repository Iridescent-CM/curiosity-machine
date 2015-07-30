# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0036_auto_20150629_0826'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='public',
            field=models.BooleanField(default=False, help_text='Public challenges are previewable without an account'),
            preserve_default=True,
        ),
    ]
