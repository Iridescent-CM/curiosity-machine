# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('images', '__first__'),
        ('videos', '__first__'),
        ('challenges', '0023_auto_20140528_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('challenge', models.ForeignKey(to_field='id', to='challenges.Challenge')),
                ('progress', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='challenges.Progress', null=True, to_field='id', blank=True, help_text="An optional association with a specific student's progress on a challenge.")),
                ('name', models.TextField(blank=True, help_text="The student's username in plain text. This can be left blank if a progress is set, in which case the progress's student username will be automatically used instead.")),
                ('image', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='images.Image', null=True, to_field='id', blank=True, help_text='An image to display in the gallery. If a video is also set, this will be the thumbnail. Each example must have an image or a video, or both, to be displayed correctly.')),
                ('video', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='videos.Video', null=True, to_field='id', blank=True, help_text='Each example must have an image or a video, or both, to be displayed correctly.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
