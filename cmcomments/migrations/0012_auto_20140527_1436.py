# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0011_auto_20140501_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='read',
            field=models.BooleanField(default=False, db_index=True),
        ),
    ]
