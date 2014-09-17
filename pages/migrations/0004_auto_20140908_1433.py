# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0003_auto_20140729_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='id',
            field=models.IntegerField(serialize=False, primary_key=True, choices=[(1, 'about'), (2, 'privacy'), (3, 'educator'), (4, 'mentor'), (5, 'parents'), (6, 'faq')]),
        ),
    ]
