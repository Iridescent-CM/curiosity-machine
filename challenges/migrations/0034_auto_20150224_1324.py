# encoding: utf8
from django.db import connection, migrations

def copy_themes(apps, schema_editor):
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO challenges_challenge_themes (challenge_id, theme_id)
        SELECT challenges_challenge.id, challenges_theme.id
        FROM challenges_challenge 
            JOIN challenges_theme
            ON challenges_challenge.theme_id = challenges_theme.id
    """)

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0033_challenge_themes'),
    ]

    operations = [
        migrations.RunPython(copy_themes, noop)
    ]
