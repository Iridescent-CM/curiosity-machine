# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(null=True, unique=True, verbose_name='name', max_length=80)),
                ('code', models.CharField(null=True, unique=True, verbose_name='code', max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
