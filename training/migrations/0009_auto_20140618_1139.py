# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0008_comment_thread'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='text',
            field=models.TextField(help_text='HTML'),
        ),
    ]
