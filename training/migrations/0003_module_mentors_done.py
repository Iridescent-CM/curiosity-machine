# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('training', '0002_comment_thread'),
    ]

    operations = [
        migrations.AddField(
            model_name='module',
            name='mentors_done',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
