# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0009_challenge_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='build_call_to_action',
            field=models.TextField(help_text='HTML', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='challenge',
            name='plan_call_to_action',
            field=models.TextField(help_text='HTML', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='how_to_make_it',
            field=models.TextField(help_text='HTML'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='learn_more',
            field=models.TextField(help_text='HTML'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='materials_list',
            field=models.TextField(help_text='HTML'),
        ),
    ]
