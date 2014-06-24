# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0024_example'),
    ]

    operations = [
        migrations.AlterField(
            model_name='theme',
            name='icon',
            field=models.TextField(max_length=64, help_text='This determines the icon that displays on the theme. Choose and icon by entering one of the following icon classes:<br><strong>icon-satellite icon-robotics icon-ocean icon-neuroscience icon-inventor icon-food icon-engineer icon-electrical icon-civil icon-builder icon-biomimicry icon-biomechanics icon-art icon-aerospace icon-compsci</strong><br /><br />Additionally available are the set of icons located here: <a href=\'http://getbootstrap.com/components/\'>Bootstrap Glyphicons</a>. Enter both class names separated with a space. for example "glyphicon glyphicon-film" without quotes.', default='icon-neuroscience'),
        ),
    ]
