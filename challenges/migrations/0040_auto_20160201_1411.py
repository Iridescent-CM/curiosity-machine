# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0039_example_approved'),
    ]

    operations = [
        migrations.AlterField(
            model_name='example',
            name='approved',
            field=models.NullBooleanField(db_index=True),
        ),
    ]
