# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0020_auto_20150518_1354'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentconnection',
            name='retries',
            field=models.PositiveSmallIntegerField(default=0),
            preserve_default=True,
        ),
    ]
