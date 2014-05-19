# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_auto_20140513_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='approved',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
