# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0021_auto_20140527_1603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='icon',
            field=models.TextField(help_text='icon class name', default='icon-neuroscience'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='color',
            field=models.TextField(help_text='color hex code or keyword', default='#84af49'),
        ),
    ]
