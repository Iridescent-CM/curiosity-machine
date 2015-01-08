# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '__first__'),
        ('challenges', '__first__'),
        ('files', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField(help_text='name of the unit')),
                ('description', models.TextField(null=True, blank=True, help_text='blurb for the unit')),
                ('overview', models.TextField(null=True, blank=True, help_text='overview for the unit')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('standards_alignment_image', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='images.Image', null=True, blank=True, to_field='id')),
                ('challenges', models.ManyToManyField(to='challenges.Challenge')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Resource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('name', models.TextField(help_text='name of the unit')),
                ('file', models.ForeignKey(blank=True, null=True, to_field='id', to='files.File', on_delete=django.db.models.deletion.SET_NULL)),
                ('unit', models.ForeignKey(to='units.Unit', to_field='id')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
