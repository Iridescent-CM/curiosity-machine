# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '__first__'),
        ('images', '__first__'),
        ('challenges', '0023_auto_20140528_1434'),
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('challenge', models.ForeignKey(to_field='id', to='challenges.Challenge')),
                ('progress', models.ForeignKey(to='challenges.Progress', to_field='id', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, help_text="An optional association with a specific student's progress on a challenge.")),
                ('_name', models.TextField(db_column='name', verbose_name='name', help_text="The student's username in plain text. This can be left blank if a progress is set, in which case the progress's student username will be automatically used instead.", blank=True)),
                ('image', models.ForeignKey(to='images.Image', to_field='id', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, help_text='An image to display in the gallery. If a video is also set, this will be the thumbnail. Each example must have an image or a video, or both, to be displayed correctly.')),
                ('video', models.ForeignKey(to='videos.Video', to_field='id', on_delete=django.db.models.deletion.SET_NULL, null=True, blank=True, help_text='Each example must have an image or a video, or both, to be displayed correctly.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
