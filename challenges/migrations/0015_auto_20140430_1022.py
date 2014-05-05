# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0014_auto_20140501_1501'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='approved',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
