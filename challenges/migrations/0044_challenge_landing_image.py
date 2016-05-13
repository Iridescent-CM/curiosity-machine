# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0043_auto_20160317_1155'),
    ]

    operations = [
        migrations.AddField(
            model_name='challenge',
            name='landing_image',
            field=models.ForeignKey(to_field='id', on_delete=django.db.models.deletion.PROTECT, null=True, blank=True, to='images.Image'),
            preserve_default=True,
        ),
    ]
