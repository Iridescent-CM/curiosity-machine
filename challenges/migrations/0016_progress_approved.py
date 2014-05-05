# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0015_remove_progress_approved'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='approved',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
