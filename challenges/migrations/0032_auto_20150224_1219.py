# encoding: utf8
from django.db import models, migrations
import challenges.validators


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0031_filter'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='color',
            field=models.TextField(max_length=64, default='#84af49', help_text='Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>', validators=[challenges.validators.validate_color]),
        ),
    ]
