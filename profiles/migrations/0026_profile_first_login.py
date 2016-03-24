# encoding: utf8
from django.db import models, migrations


def set_first_login(apps, schema_editor):
    Profile = apps.get_model("profiles", "Profile")
    Profile.objects.filter(shown_intro=False).update(first_login=True)
    
class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0025_auto_20151117_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='first_login',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
        migrations.RunPython(set_first_login),
    ]
