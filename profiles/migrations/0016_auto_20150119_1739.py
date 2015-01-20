# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0015_profile_expertise'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='expertise',
            field=models.TextField(help_text='This is a mentor only field.', blank=True, null=True),
        ),
    ]
