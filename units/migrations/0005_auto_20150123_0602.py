# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '__first__'),
        ('units', '0004_remove_unit_challenges'),
    ]

    operations = [
        migrations.CreateModel(
            name='UnitChallenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('unit', models.ForeignKey(to_field='id', to='units.Unit')),
                ('challenge', models.ForeignKey(to_field='id', to='challenges.Challenge')),
                ('order', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='unit',
            name='challenges',
            field=models.ManyToManyField(to='challenges.Challenge', null=True, blank=True, through='units.UnitChallenge'),
            preserve_default=True,
        ),
    ]
