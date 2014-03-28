# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0002_auto_20140325_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='mentor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id', null=True),
            preserve_default=True,
        ),
    ]
