# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0037_challenge_public'),
    ]

    operations = [
        migrations.AddField(
            model_name='filter',
            name='header_template',
            field=models.CharField(blank=True, max_length=128, help_text='Path to template containing header to display on filtered view', null=True),
            preserve_default=True,
        ),
    ]
