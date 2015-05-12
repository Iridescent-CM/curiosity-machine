# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0018_auto_20150205_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_parent',
            field=models.BooleanField(default=False, verbose_name='Parent leader access'),
            preserve_default=True,
        ),
    ]
