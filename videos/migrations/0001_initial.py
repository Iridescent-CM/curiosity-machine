# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('video', models.URLField(max_length=2083, blank=True, null=True)),
                ('unique_hash', models.CharField(max_length=40)),
                ('encoding_id', models.IntegerField(blank=True, null=True)),
                ('encodings_generated', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OutputVideo',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('video', models.URLField(max_length=2083, blank=True, null=True)),
                ('base_video', models.ForeignKey(to='videos.Video', to_field='id')),
                ('md5_checksum', models.CharField(max_length=32, blank=True)),
                ('output_id', models.IntegerField()),
                ('width', models.IntegerField(default=0)),
                ('height', models.IntegerField(default=0)),
                ('frame_rate', models.IntegerField(default=0)),
                ('duration_in_ms', models.IntegerField(default=0)),
                ('video_codec', models.CharField(max_length=10, blank=True)),
                ('format', models.CharField(max_length=10, blank=True)),
                ('audio_codec', models.CharField(max_length=10, blank=True)),
                ('size', models.IntegerField(default=0)),
                ('video_bitrate_in_kbps', models.IntegerField(default=0)),
                ('audio_bitrate_in_kbps', models.IntegerField(default=0)),
                ('total_bitrate_in_kbps', models.IntegerField(default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
