# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0003_module_mentors_done'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='mentors_done',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, null=True, blank=True),
        ),
    ]
