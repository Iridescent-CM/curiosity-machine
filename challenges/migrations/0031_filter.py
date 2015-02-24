# encoding: utf8
from django.db import models, migrations
import challenges.validators


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0030_auto_20141202_0835'),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='name of the filter', max_length=50)),
                ('color', models.CharField(help_text='Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>', max_length=7, validators=[challenges.validators.validate_color], blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('visible', models.BooleanField(db_index=True, default=False)),
                ('challenges', models.ManyToManyField(to='challenges.Challenge')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
