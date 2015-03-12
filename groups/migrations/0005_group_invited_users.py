# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0004_invitation'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='invited_users',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='groups.Invitation', null=True),
            preserve_default=True,
        ),
    ]
