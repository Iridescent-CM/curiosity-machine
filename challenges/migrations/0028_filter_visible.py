# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_filter'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='visible',
            field=models.BooleanField(db_index=True, default=False),
            preserve_default=True,
        ),
    ]
