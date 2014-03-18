# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='location',
            new_name='city',
        ),
        migrations.AddField(
            model_name='profile',
            name='parent_first_name',
            field=models.CharField(blank=True, null=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='parent_last_name',
            field=models.CharField(blank=True, null=True, max_length=64),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='nickname',
            field=models.CharField(blank=True, null=True, max_length=64),
            preserve_default=True,
        ),
    ]
