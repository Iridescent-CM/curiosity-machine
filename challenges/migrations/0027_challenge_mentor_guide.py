# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0026_auto_20140630_0708'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='mentor_guide',
            field=models.TextField(null=True, help_text='HTML, shown in the mentor guide'),
            preserve_default=True,
        ),
    ]
