# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0029_auto_20160512_1407'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='is_parent',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_mentor',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_educator',
        ),
        migrations.RemoveField(
            model_name='profile',
            name='is_student',
        ),
    ]
