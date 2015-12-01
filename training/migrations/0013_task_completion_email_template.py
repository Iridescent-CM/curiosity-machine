# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0012_make_modules_non_draft'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completion_email_template',
            field=models.CharField(help_text='Optional template name to send on task completion', blank=True, max_length=70, null=True),
            preserve_default=True,
        ),
    ]
