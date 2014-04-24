# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0007_auto_20140424_1506'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='materials_list',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
