# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-06-08 15:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inspiration', models.TextField(blank=True)),
                ('plan', models.TextField(blank=True)),
                ('build', models.TextField(blank=True)),
                ('further', models.TextField(blank=True)),
            ],
        ),
    ]