# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0011_auto_20141210_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='shown_intro',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
