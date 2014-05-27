# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0020_auto_20140523_1556'),
    ]

    operations = [
        migrations.AddField(
            model_name='theme',
            name='icon',
            field=models.CharField(max_length=64, default='icon-neuroscience', help_text='icon class name'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='theme',
            name='color',
            field=models.CharField(max_length=64, default='#84af49', help_text='color hex code or keyword'),
            preserve_default=True,
        ),
    ]
