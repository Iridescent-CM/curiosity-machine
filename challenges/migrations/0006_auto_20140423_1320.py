# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('challenges', '0005_challenge_video'),
    ]

    operations = [
        migrations.AddField(
            model_name='progress',
            name='mentor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, to_field='id'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='challenge',
            name='mentor',
        ),
    ]
