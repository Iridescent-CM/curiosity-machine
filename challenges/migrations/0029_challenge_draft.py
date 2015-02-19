# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0028_auto_20150203_1451'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='draft',
            field=models.BooleanField(default=True, help_text='Draft'),
            preserve_default=True,
        ),
    ]
