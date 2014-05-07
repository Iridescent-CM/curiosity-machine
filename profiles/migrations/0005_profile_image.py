# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20140324_1601'),
        ('images', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='image',
            field=models.ForeignKey(to='images.Image', blank=True, to_field='id', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
