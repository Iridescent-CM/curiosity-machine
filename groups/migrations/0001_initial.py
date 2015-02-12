# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('name', models.CharField(unique=True, null=True, max_length=80, verbose_name='name')),
                ('code', models.CharField(unique=True, null=True, max_length=20, verbose_name='code')),
            ],
            options={
                'verbose_name': 'group',
                'verbose_name_plural': 'groups',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('group', models.ForeignKey(to_field='id', to='groups.Group')),
                ('profile', models.ForeignKey(to_field='id', to='profiles.Profile')),
                ('role', models.SmallIntegerField(choices=[(0, 'owner'), (1, 'member')], default=0)),
            ],
            options={
                'verbose_name': 'membership',
                'verbose_name_plural': 'membership',
            },
            bases=(models.Model,),
        ),
    ]
