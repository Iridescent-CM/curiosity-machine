# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0022_auto_20150629_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='source',
            field=models.CharField(null=True, max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
