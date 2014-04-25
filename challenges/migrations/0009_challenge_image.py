# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0008_challenge_materials_list'),
        ('images', '__first__'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='image',
            field=models.ForeignKey(to='images.Image', blank=True, null=True, to_field='id'),
            preserve_default=True,
        ),
    ]
