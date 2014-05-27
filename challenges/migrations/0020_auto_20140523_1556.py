# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0019_auto_20140523_1548'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='description',
            field=models.TextField(help_text='One line of plain text, shown on the inspiration page'),
        ),
    ]
