# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0024_auto_20151117_1605'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='source',
            field=models.CharField(max_length=50, blank=True, default=''),
        ),
    ]
