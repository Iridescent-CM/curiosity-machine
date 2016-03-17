# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0042_auto_20160309_1040'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='example',
            name='challenge',
        ),
        migrations.AlterField(
            model_name='example',
            name='progress',
            field=models.ForeignKey(to='challenges.Progress', to_field='id'),
        ),
    ]
