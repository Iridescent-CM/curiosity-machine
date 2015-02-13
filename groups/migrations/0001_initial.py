# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='name', null=True)),
                ('code', models.CharField(max_length=20, unique=True, verbose_name='code', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
