# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_challenge_mentor_guide'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', auto_created=True, primary_key=True)),
                ('name', models.TextField(help_text='name of the filter')),
                ('color', models.TextField(help_text='a hex color like 44b1cc', null=True, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(db_index=True, default=False)),
                ('challenges', models.ManyToManyField(to='challenges.Challenge')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
