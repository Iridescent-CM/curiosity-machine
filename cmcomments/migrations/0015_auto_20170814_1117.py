# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
from notifications.signals import notify
from django.contrib.auth import get_user_model


def make_notifications(apps, schema_editor):
    Comment = apps.get_model("cmcomments", "Comment")
    User = get_user_model()
    for comment in Comment.objects.filter(read=False, challenge_progress__mentor_id__isnull=False).all():
        progress = comment.challenge_progress
        if comment.user == progress.mentor:
            recipient = progress.student
        elif comment.user == progress.student:
            recipient = progress.mentor
        recipient = User.objects.get(id=recipient.id) # notify doesn't like the recipient object type otherwise
        notify.send(comment.user, recipient=recipient, verb="posted", action_object=comment, target=progress, timestamp=comment.created)

class Migration(migrations.Migration):

    dependencies = [
        ('cmcomments', '0014_auto_20160506_1138'),
        ('notifications', '0005_auto_20160504_1520'),
    ]

    operations = [
        migrations.RunPython(make_notifications)
    ]
