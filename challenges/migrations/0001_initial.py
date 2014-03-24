# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Challenge',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('how_to_make_it', models.TextField()),
                ('learn_more', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
