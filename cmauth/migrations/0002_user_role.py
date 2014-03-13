# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmauth', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.SmallIntegerField(choices=[(1, 1), (2, 2)], default=2),
            preserve_default=True,
        ),
    ]
