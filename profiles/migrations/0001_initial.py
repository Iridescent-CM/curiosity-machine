# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('user', models.OneToOneField(null=True, to=settings.AUTH_USER_MODEL, to_field='id')),
                ('birthday', models.DateField(null=True, blank=True)),
                ('gender', models.CharField(max_length=1, blank=True)),
                ('location', models.CharField(max_length=128, blank=True)),
                ('occupation', models.CharField(max_length=255, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
