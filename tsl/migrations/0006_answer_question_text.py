# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tsl', '0005_auto_20140916_1000'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='question_text',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]
