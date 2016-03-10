# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0041_auto_20160308_1600'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='example',
            name='video',
        ),
        migrations.RemoveField(
            model_name='example',
            name='_name',
        ),
    ]
