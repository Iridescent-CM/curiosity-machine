# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0034_auto_20150224_1324'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='challenge',
            name='theme',
        ),
    ]
