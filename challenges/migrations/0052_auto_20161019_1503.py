# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0051_challenge_core'),
    ]

    operations = [
        migrations.AlterField(
            model_name='resource',
            name='challenge',
            field=models.ForeignKey(help_text='The challenge that this resource should be associated with.', null=True, to='challenges.Challenge'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='description',
            field=models.TextField(help_text='Text that describes the resource. Should be < 50 words.'),
        ),
        migrations.AlterField(
            model_name='resource',
            name='name',
            field=models.CharField(max_length=128, help_text='Title for the resource, e.g. “Grade 3-5 Mini Unit”.'),
        ),
        migrations.AlterField(
            model_name='resourcefile',
            name='link_text',
            field=models.CharField(max_length=64, null=True, help_text='Text that goes on a button. Keep it short (1 - 3 words).'),
        ),
    ]
