# encoding: utf8
from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_auto_20140317_1718'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_mentor',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='title',
            field=models.TextField(blank=True, default=''),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='profile',
            name='occupation',
        ),
        migrations.AlterField(
            model_name='profile',
            name='city',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL, to_field='id'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='parent_last_name',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='nickname',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='parent_first_name',
            field=models.TextField(blank=True),
        ),
    ]
