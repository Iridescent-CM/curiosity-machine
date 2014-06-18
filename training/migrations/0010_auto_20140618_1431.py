# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0009_auto_20140618_1139'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='image',
            field=models.ForeignKey(blank=True, to_field='id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='module',
            name='image',
            field=models.ForeignKey(blank=True, to_field='id', null=True, on_delete=django.db.models.deletion.SET_NULL, to='images.Image'),
            preserve_default=True,
        ),
    ]
