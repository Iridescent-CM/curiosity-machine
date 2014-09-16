# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('tsl', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('question', models.ForeignKey(to='tsl.Question', to_field='id')),
                ('answer_text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
