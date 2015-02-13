# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('group', models.ForeignKey(to='groups.Group', to_field='id')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('role', models.SmallIntegerField(default=0, choices=[(0, 'Educator'), (1, 'Student')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
