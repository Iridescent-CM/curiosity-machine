# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('filepicker_url', models.TextField(blank=True)),
                ('md5_hash', models.CharField(max_length=32, blank=True)),
                ('filename', models.CharField(max_length=1024, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
