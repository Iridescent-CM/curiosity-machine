# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_membership'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='member_users',
            field=models.ManyToManyField(through='groups.Membership', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
