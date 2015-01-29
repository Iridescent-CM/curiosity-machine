# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_auto_20150120_0934'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='expertise',
            field=models.TextField(help_text='This is a mentor only field.', default='', blank=True),
            preserve_default=False,
        ),
    ]
