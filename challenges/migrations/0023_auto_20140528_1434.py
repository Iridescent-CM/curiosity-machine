# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0022_auto_20140527_1622'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='icon',
            field=models.TextField(default='icon-neuroscience', max_length=64, help_text='This determines the icon that displays on the theme. Choose and icon by entering one of the following icon classes:<br><strong>icon-satellite icon-robotics icon-ocean icon-neuroscience icon-inventor icon-food icon-engineer icon-electrical icon-civil icon-builder icon-biomimicry icon-biomechanics icon-art icon-aerospace</strong><br /><br />Additionally available are the set of icons located here: <a href=\'http://getbootstrap.com/components/\'>Bootstrap Glyphicons</a>. Enter both class names separated with a space. for example "glyphicon glyphicon-film" without quotes.'),
        ),
        migrations.AlterField(
            model_name='theme',
            name='color',
            field=models.TextField(default='#84af49', max_length=64, help_text='Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>'),
        ),
    ]
