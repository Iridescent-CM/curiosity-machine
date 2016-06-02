# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('memberships', '0003_member_membership'),
    ]

    operations = [
        migrations.AddField(
            model_name='membership',
            name='educator_limit',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='membership',
            name='student_limit',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
