# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0013_auto_20141216_1041'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_student',
            field=models.BooleanField(default=False, verbose_name='Student access'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='is_mentor',
            field=models.BooleanField(default=False, verbose_name='Mentor access'),
        ),
    ]
