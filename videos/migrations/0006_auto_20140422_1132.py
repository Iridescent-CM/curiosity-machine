# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0005_video_raw_job_detalis'),
    ]

    operations = [
        migrations.RenameField(
            model_name='video',
            old_name='raw_job_detalis',
            new_name='raw_job_details',
        ),
    ]
