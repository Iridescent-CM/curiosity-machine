# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0017_progress_materials_list'),
    ]

    operations = [
        migrations.RenameField(
            model_name='progress',
            old_name='materials_list',
            new_name='_materials_list',
        ),
        migrations.AlterField(
            model_name='progress',
            name='_materials_list',
            field=models.TextField(db_column='materials_list', blank=True, help_text='HTML'),
        ),
    ]
