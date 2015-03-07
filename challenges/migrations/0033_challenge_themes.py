# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0032_auto_20150224_1219'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='themes',
            field=models.ManyToManyField(to='challenges.Theme', blank=True, null=True),
            preserve_default=True,
        ),
    ]
