# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0026_auto_20140630_0708'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChallengeClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('challenge', models.ForeignKey(to='challenges.Challenge', to_field='id')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ChallengeTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.TextField(help_text='name of the filter')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('challenges', models.ManyToManyField(to='challenges.Challenge', through='challenges.ChallengeClassification')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
