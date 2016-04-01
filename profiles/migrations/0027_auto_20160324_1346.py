# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0026_profile_first_login'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='shown_intro',
        ),
        migrations.AlterField(
            model_name='profile',
            name='first_login',
            field=models.BooleanField(default=True),
        ),
    ]
