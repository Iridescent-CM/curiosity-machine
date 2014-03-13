# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('mentor', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('student', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('challenge', models.ForeignKey(to='challenges.Challenge', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('conversation', models.ForeignKey(to='cmmessages.Conversation', blank=True, to_field='id')),
                ('sender', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('recipient', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('challenge', models.ForeignKey(to='challenges.Challenge', to_field='id')),
                ('text', models.TextField()),
                ('read', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
