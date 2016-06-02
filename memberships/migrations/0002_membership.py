# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '__first__'),
        ('memberships', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('name', models.CharField(max_length=255, unique=True)),
                ('expiration', models.DateField(blank=True, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('challenges', models.ManyToManyField(to='challenges.Challenge', blank=True, null=True)),
                ('members', models.ManyToManyField(through='memberships.Member', to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
