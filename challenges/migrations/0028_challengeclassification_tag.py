# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0027_challengeclassification_challengetag'),
    ]

    operations = [
        migrations.AddField(
            model_name='challengeclassification',
            name='tag',
            field=models.ForeignKey(to='challenges.ChallengeTag', to_field='id'),
            preserve_default=True,
        ),
    ]
