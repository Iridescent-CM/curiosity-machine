# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0006_module'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('module', models.ForeignKey(to='training.Module', to_field='id')),
                ('order', models.PositiveSmallIntegerField(help_text='The order, starting from 1, in which this module will be displayed. The URL to the task page is based on this number, so changing it will also change the URL. The numbers must be unique within a single module. The numbers should also be sequential within a single module.')),
                ('name', models.CharField(max_length=70)),
                ('text', models.TextField()),
                ('mentors_done', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('module', 'order'),
                'unique_together': set([('module', 'order')]),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('task', models.ForeignKey(to='training.Task', to_field='id')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, to_field='id')),
                ('text', models.TextField()),
                ('created', models.DateTimeField(default=django.utils.timezone.now)),
                ('image', models.ForeignKey(null=True, to_field='id', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='images.Image')),
                ('video', models.ForeignKey(null=True, to_field='id', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='videos.Video')),
            ],
            options={
                'ordering': ('created',),
            },
            bases=(models.Model,),
        ),
    ]
