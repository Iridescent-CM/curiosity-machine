# encoding: utf8
from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0044_challenge_landing_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='challenge',
            name='landing_image',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.PROTECT, null=True, to_field='id', to='images.Image', help_text='Image size should be a 4:3 ratio, at least 720px wide for best results. Jpg, png, or gif accepted.'),
        ),
    ]
