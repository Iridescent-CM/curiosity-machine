# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0006_auto_20140423_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='materials_list',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
