from django.conf import settings
from zencoder import Zencoder
import datetime
import django_rq
import requests
import tinys3
import tempfile
from .models import Video, EncodedVideo
from images.models import Image
from django.db import IntegrityError

TIME_BETWEEN_STATUS_CHECKS = datetime.timedelta(minutes=1)

def encode_video(video):
    client = Zencoder(settings.ZENCODER_API_KEY)
    client.account.live() # don't run in integration mode by mistake -- this line factors out the biggest remote state issue
    response = client.job.create(video.url,
        outputs=[{'format': 'mp4', 'thumbnails': [{'label': 'thumbnail','format': 'jpg', 'number': 4,}]},
                 {'format': 'ogg'}])
    check_video_job_progress(video, response.body['id'])

def check_video_job_progress(video, job_id): # repeats itself every TIME_BETWEEN_STATUS_CHECKS until all outputs are done or dead
    client = Zencoder(settings.ZENCODER_API_KEY)
    job = client.job.details(job_id)

    #record the raw job details in the database -- use update() here in order to avoid any concurrency problems if the video obj is stale
    Video.objects.filter(id=video.id).update(raw_job_details=str(job.body))

    outputs = job.body['job']["output_media_files"]
    unfinished = False
    for output in outputs:
        if output['state'] == "finished":
            django_rq.enqueue(handle_finished_video_output, video, output)
        elif output['state'] not in ["failed", "cancelled", "no input"]:
            unfinished = True

    if unfinished:
        scheduler = django_rq.get_scheduler()
        scheduler.enqueue_in(TIME_BETWEEN_STATUS_CHECKS, check_video_job_progress, video, job_id)
    else:
        #add thumbnails as images
        for thumbnail in job.body['job']['thumbnails']:
            video.thumbnails.add(Image.from_source_with_job(thumbnail['url']))

def handle_finished_video_output(video, output):
    # zencoder docs are inconsistent on whether they use mpeg4 or mp4, so may as well normalize here
    output_format = output['format'] if output['format'] != "mpeg4" else "mp4" 
    mime_type = "video/{}".format(output_format)
    height, width = output['height'], output['width']
    if EncodedVideo.objects.filter(video_id=video.id, height=height, width=width, mime_type=mime_type):
        return # if this combination already exists, do nothing successfully

    response = requests.get(output['url'])
    conn = tinys3.Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, tls=True)

    encoding = EncodedVideo(video=video, height=output['height'], width=output['width'], mime_type=mime_type, raw_encoding_details=str(output))

    with tempfile.TemporaryFile() as fd:
        for chunk in response.iter_content(1024*1024): # write with 1MB chunks -- not sure if there is any significant performance impact here though
            fd.write(chunk)
        fd.seek(0) # reset to beginning of file for reading
        key = "videos/{key}.{format}".format(key=video.key, format=output_format)
        conn.upload(key, fd, settings.AWS_STORAGE_BUCKET_NAME, public=True) # upload to AWS_STORAGE_BUCKET_NAME with the hash as the key
        encoding.key = key # now that it's uploaded, set the filename to the model too

    try:
        encoding.save()
    except IntegrityError: # race condition -- this encoding combo already exists. just do nothing here.
        return
