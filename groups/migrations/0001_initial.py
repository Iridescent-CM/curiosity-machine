# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(null=True, verbose_name='name', max_length=80)),
                ('code', models.CharField(null=True, verbose_name='code', unique=True, max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
