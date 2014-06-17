# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('training', '0005_auto_20140617_1601'),
    ]

    operations = [
        migrations.CreateModel(
            name='Module',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('order', models.PositiveSmallIntegerField(help_text="The order, starting from 1, in which this module will be displayed. The URL to the module page and all of the module's task pages are based on this number, so changing it will also change the URLs. This also affects trainee progression -- for instance, the first module is always available to trainees, and a trainee who completes all tasks in the lastly-ordered module is promoted to mentor ('approved'). The numbers should be sequential.", unique=True)),
                ('name', models.CharField(max_length=70)),
            ],
            options={
                'ordering': ('order',),
            },
            bases=(models.Model,),
        ),
    ]
