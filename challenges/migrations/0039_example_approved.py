# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0038_filter_header_template'),
    ]

    operations = [
        migrations.AddField(
            model_name='example',
            name='approved',
            field=models.BooleanField(default=True, db_index=True),
            preserve_default=False,
        ),
    ]
