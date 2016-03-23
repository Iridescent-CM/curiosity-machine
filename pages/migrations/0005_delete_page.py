# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0004_auto_20140908_1433'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Page',
        ),
    ]
