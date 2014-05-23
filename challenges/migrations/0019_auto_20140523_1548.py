# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0018_auto_20140520_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='build_subheader',
            field=models.TextField(help_text='One line of plain text, shown below the build stage header', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='challenge',
            name='plan_subheader',
            field=models.TextField(help_text='One line of plain text, shown below the plan stage header', default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='challenge',
            name='reflect_subheader',
            field=models.TextField(help_text='One line of plain text, shown below the reflect stage header', default=''),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='challenge',
            name='learn_more',
            field=models.TextField(help_text='HTML, shown in the guide'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='build_call_to_action',
            field=models.TextField(help_text='HTML, shown in the left column of the build stage'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='plan_call_to_action',
            field=models.TextField(help_text='HTML, shown in the left column of the plan stage'),
        ),
        migrations.AlterField(
            model_name='challenge',
            name='how_to_make_it',
            field=models.TextField(help_text='HTML, shown in the guide'),
        ),
    ]
