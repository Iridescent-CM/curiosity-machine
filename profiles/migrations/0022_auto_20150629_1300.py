# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0021_parentconnection_retries'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_parent',
            field=models.BooleanField(default=False, verbose_name='Parent access'),
        ),
    ]
