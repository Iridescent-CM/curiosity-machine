# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('videos', '0002_outputvideo_thumbnail'),
    ]

    operations = [
        migrations.CreateModel(
            name='EncodedVideo',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('video', models.ForeignKey(to_field='id', to='videos.Video')),
                ('key', models.CharField(max_length=1024)),
                ('width', models.IntegerField()),
                ('height', models.IntegerField()),
                ('mime_type', models.CharField(max_length=255)),
                ('raw_encoding_details', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.DeleteModel(
            name='OutputVideo',
        ),
        migrations.AddField(
            model_name='video',
            name='md5_hash',
            field=models.CharField(blank=True, default='', max_length=32),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='key',
            field=models.CharField(blank=True, default='', max_length=1024),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='video',
            name='source_url',
            field=models.URLField(blank=True, default='', max_length=2048),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='video',
            name='unique_hash',
        ),
        migrations.RemoveField(
            model_name='video',
            name='encodings_generated',
        ),
        migrations.RemoveField(
            model_name='video',
            name='video',
        ),
        migrations.RemoveField(
            model_name='video',
            name='encoding_id',
        ),
    ]
