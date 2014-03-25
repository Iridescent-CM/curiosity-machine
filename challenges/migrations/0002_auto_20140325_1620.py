# encoding: utf8
from django.db import models, migrations
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('challenges', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Progress',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('challenge', models.ForeignKey(to_field='id', to='challenges.Challenge')),
                ('student', models.ForeignKey(to_field='id', to=settings.AUTH_USER_MODEL)),
                ('started', models.DateTimeField(default=django.utils.timezone.now)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='challenge',
            name='students',
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL, through='challenges.Progress'),
            preserve_default=True,
        ),
    ]
