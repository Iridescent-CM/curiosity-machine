# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0028_filter_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='color',
            field=models.TextField(null=True, help_text='a hex color like 44b1cc', blank=True),
            preserve_default=True,
        ),
    ]
