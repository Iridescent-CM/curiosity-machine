# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0016_profile_expertise'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_educator',
            field=models.BooleanField(default=False, verbose_name='Educator access'),
            preserve_default=True,
        ),
    ]
