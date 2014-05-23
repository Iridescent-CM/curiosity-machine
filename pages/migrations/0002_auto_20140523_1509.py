# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='id',
            field=models.IntegerField(choices=[(1, 'about'), (2, 'privacy')], serialize=False, primary_key=True),
        ),
    ]
