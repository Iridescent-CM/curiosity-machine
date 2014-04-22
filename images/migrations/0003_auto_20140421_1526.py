# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('images', '0002_auto_20140421_1525'),
    ]

    operations = [
        migrations.RenameField(
            model_name='image',
            old_name='filename',
            new_name='key',
        ),
    ]
