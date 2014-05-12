# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_profile_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='about_research',
            field=models.TextField(null=True, help_text='This is a mentor only field.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='about_me',
            field=models.TextField(null=True, help_text='This is a mentor only field.', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='employer',
            field=models.TextField(null=True, help_text='This is a mentor only field.', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='profile',
            name='title',
            field=models.TextField(help_text='This is a mentor only field.', blank=True),
        ),
    ]
