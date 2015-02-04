# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_challenge_mentor_guide'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='mentor_guide',
            field=models.TextField(help_text='HTML, shown in the mentor guide', blank=True, null=True),
        ),
    ]
