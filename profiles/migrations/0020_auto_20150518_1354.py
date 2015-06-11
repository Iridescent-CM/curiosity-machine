# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0019_profile_is_parent'),
    ]

    operations = [
        migrations.CreateModel(
            name='ParentConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('parent_profile', models.ForeignKey(to='profiles.Profile', to_field='id')),
                ('child_profile', models.ForeignKey(to='profiles.Profile', to_field='id')),
                ('active', models.BooleanField(default=False)),
                ('removed', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='profile',
            name='child_profiles',
            field=models.ManyToManyField(to='profiles.Profile', null=True, through='profiles.ParentConnection'),
            preserve_default=True,
        ),
    ]
