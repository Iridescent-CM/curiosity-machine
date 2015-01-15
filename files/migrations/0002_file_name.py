# encoding: utf8
from django.db import models, migrations
from datetime import date


class Migration(migrations.Migration):

    dependencies = [
        ('files', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='file',
            name='name',
            field=models.TextField(default=date(2015, 1, 15), help_text='name of the file'),
            preserve_default=False,
        ),
    ]
