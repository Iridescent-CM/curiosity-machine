# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0016_progress_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='materials_list',
            field=models.TextField(help_text='HTML', default='', blank=True),
            preserve_default=False,
        ),
    ]
