# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('source_url', models.URLField(blank=True, max_length=2048)),
                ('md5_hash', models.CharField(blank=True, max_length=32)),
                ('key', models.CharField(blank=True, max_length=1024)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
