# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.IntegerField(choices=[(1, 'about')], serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=70, help_text='title of the page, in one line of plain text')),
                ('text', models.TextField(help_text='contents of the page, in HTML')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
