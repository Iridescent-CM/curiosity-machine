# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('challenges', '0025_auto_20140624_1602'),
    ]

    operations = [
        migrations.CreateModel(
            name='Favorite',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('challenge', models.ForeignKey(to_field='id', to='challenges.Challenge')),
                ('student', models.ForeignKey(to_field='id', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Favorites',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='challenge',
            name='favorited',
            field=models.ManyToManyField(null=True, through='challenges.Favorite', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
