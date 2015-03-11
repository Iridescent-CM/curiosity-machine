# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('groups', '0003_group_members'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('group', models.ForeignKey(to='groups.Group', to_field='id')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
            ],
            options={
                'unique_together': set([('group', 'user')]),
            },
            bases=(models.Model,),
        ),
    ]
