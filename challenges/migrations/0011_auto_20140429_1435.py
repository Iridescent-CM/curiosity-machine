# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0010_auto_20140429_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='reflect_question',
            field=models.TextField(default='', help_text='HTML'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='progress',
            name='approved',
            field=models.BooleanField(default=False, help_text='true when the mentor has approved a completed challenge and moved it to the reflect stage'),
            preserve_default=True,
        ),
    ]
