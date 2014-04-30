# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0009_auto_20140428_1344'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='question_text',
            field=models.TextField(help_text='If the comment is in direct reply to a question, this will contain the full text of the question.', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='stage',
            field=models.SmallIntegerField(choices=[(1, 'plan'), (2, 'build'), (3, 'test'), (4, 'reflect')], default=2),
        ),
    ]
