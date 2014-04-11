from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.conf import settings
from challenges.models import Challenge, Progress
from cmcomments.models import Comment
from cmcomments.forms import CommentForm
from curiositymachine.decorators import mentor_or_current_student
from urllib.request import urlretrieve
import django_rq
import uuid
import os
from boto.s3.connection import S3Connection
from boto.s3.key import Key

# refactor input into decorators
@login_required
@mentor_or_current_student
def comments(request, challenge_id, username, format=None):
    challenge = get_object_or_404(Challenge, id=challenge_id)
    progress = get_object_or_404(Progress, challenge=challenge, student__username=username)
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            comment = Comment(user=request.user, text=form.cleaned_data['text'], challenge_progress=progress, image=form.cleaned_data['picture_filepicker_url'])
            comment.save()
            if comment.image:
                django_rq.enqueue(upload_filepicker_image, comment)
        #TODO: add some way to handle form.errors, for instance converting it into a JSON API

    return HttpResponseRedirect(reverse('challenges:challenge_progress', kwargs={'challenge_id': challenge.id, 'username': username,}))

def upload_filepicker_image(comment):
    image_url = comment.image
    path, header = urlretrieve(image_url)
    s3_connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3_connection.create_bucket(settings.AWS_MEDIA_S3_BUCKET_NAME)
    unique_hash = str(uuid.uuid4())
    while bucket.get_key(unique_hash):
        unique_hash = str(uuid.uuid4())
    k = Key(bucket)
    k.key = unique_hash
    k.set_contents_from_filename(path)
    k.set_acl('public-read')
    comment.image = 'https://%s.s3.amazonaws.com/%s' % (settings.AWS_MEDIA_S3_BUCKET_NAME, unique_hash)
    comment.save()
