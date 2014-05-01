# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0013_challenge_reflect_questions'),
    ]

    operations = [
        migrations.AlterField(
            model_name='progress',
            name='mentor',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='video',
            field=models.ForeignKey(to='videos.Video', to_field='id', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='image',
            field=models.ForeignKey(to='images.Image', to_field='id', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='theme',
            field=models.ForeignKey(to='challenges.Theme', to_field='id', blank=True, on_delete=django.db.models.deletion.SET_NULL, null=True),
        ),
    ]
