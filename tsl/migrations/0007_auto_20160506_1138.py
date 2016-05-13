# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tsl', '0006_answer_question_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='answer',
            name='image',
            field=models.ForeignKey(null=True, related_name='answer', blank=True, to='images.Image', on_delete=django.db.models.deletion.SET_NULL),
        ),
        migrations.AlterField(
            model_name='answer',
            name='video',
            field=models.ForeignKey(null=True, related_name='answer', blank=True, to='videos.Video', on_delete=django.db.models.deletion.SET_NULL),
        ),
    ]
