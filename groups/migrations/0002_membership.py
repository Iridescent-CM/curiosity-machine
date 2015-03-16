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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('group', models.ForeignKey(to_field='id', to='groups.Group')),
                ('user', models.ForeignKey(to_field='id', to=settings.AUTH_USER_MODEL)),
                ('role', models.SmallIntegerField(choices=[(0, 'Owner'), (1, 'Member')], default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
