# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0048_resource_resourcefile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='challenge',
            options={'ordering': ['order']},
        ),
        migrations.AddField(
            model_name='challenge',
            name='order',
            field=models.PositiveIntegerField(blank=True, verbose_name='Order preference', help_text='Challenges will be shown in ascending numeric order, with blanks last', null=True),
        ),
    ]