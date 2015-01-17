# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_auto_20150108_1044'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='expertise',
            field=models.TextField(blank=True, default=None, help_text='This is a mentor only field.'),
            preserve_default=False,
        ),
    ]
