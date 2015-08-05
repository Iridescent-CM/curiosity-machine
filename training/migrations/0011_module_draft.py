# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0010_auto_20140618_1431'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='draft',
            field=models.BooleanField(help_text='Drafts are not shown on the mentor home page', default=True),
            preserve_default=True,
        ),
    ]
