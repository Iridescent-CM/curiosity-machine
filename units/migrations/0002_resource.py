# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('files', '__first__'),
        ('units', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.TextField(help_text='name of the unit')),
                ('file', models.ForeignKey(blank=True, null=True, to_field='id', to='files.File', on_delete=django.db.models.deletion.SET_NULL)),
                ('unit', models.ForeignKey(to='units.Unit', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
