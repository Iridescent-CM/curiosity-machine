# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0012_auto_20140501_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='reflect_questions',
            field=models.ManyToManyField(to='challenges.Question', null=True),
            preserve_default=True,
        ),
    ]
