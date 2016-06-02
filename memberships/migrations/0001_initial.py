# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
