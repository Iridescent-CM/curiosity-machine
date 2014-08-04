# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0002_auto_20140523_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='id',
            field=models.IntegerField(primary_key=True, serialize=False, choices=[(1, 'about'), (2, 'privacy'), (3, 'educator'), (4, 'mentor'), (5, 'parents')]),
        ),
    ]
