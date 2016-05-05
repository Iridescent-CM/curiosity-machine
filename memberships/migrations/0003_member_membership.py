# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0002_membership'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='membership',
            field=models.ForeignKey(to='memberships.Membership', to_field='id'),
            preserve_default=True,
        ),
    ]
