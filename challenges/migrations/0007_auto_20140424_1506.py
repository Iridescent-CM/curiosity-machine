# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0006_auto_20140423_1320'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='mentor',
            field=models.ForeignKey(blank=True, null=True, to_field='id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='theme',
            field=models.ForeignKey(blank=True, null=True, to_field='id', to='challenges.Theme'),
        ),
    ]
