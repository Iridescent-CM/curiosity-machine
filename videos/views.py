from django.shortcuts import render
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import uuid
from copy import deepcopy
from zencoder import Zencoder
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from urllib.request import urlretrieve
from videos.models import Video, OutputVideo
from cmcomments.output_settings import OUTPUTS

def upload_filepicker_video(comment):
    video_url = comment.video.video
    path, header = urlretrieve(video_url)
    s3_connection = S3Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
    bucket = s3_connection.create_bucket(settings.AWS_MEDIA_S3_BUCKET_NAME)
    unique_hash = str(uuid.uuid4())
    while bucket.get_key(unique_hash):
        unique_hash = str(uuid.uuid4())
    k = Key(bucket)
    k.key = unique_hash
    k.set_contents_from_filename(path)
    k.set_acl('public-read')
    comment.video.video = 'https://%s.s3.amazonaws.com/%s' % (settings.AWS_MEDIA_S3_BUCKET_NAME, unique_hash)
    print(unique_hash)
    comment.video.unique_hash = unique_hash
    comment.video.save()
    generate_encodings(comment.video)

def generate_encodings(video):
    client = Zencoder(settings.ZENCODER_API_KEY)
    outputs = []
    for op in OUTPUTS:
        output_copy = deepcopy(op)
        output_copy['url'] = 's3://%s%s-%dx%d%s' % (settings.ZENCODER_S3_BUCKET, video.unique_hash, op['width'], op['height'], op['url'])
        output_copy['thumbnails']['base_url'] += '%s/' % video.unique_hash
        outputs.append(output_copy)
    input_url = 's3://%s/%s' % (settings.AWS_MEDIA_S3_BUCKET_NAME, video.unique_hash)
    try:
        response = client.job.create(input_url, outputs=outputs)
    except:
        print('Error creating zencoder job')
        # TODO: re-try job
        return
    if response.code == 201:
        print(response.body['id'])
    else:
        print(response.body, response.code)
    video.encoding_id = response.body['id']
    video.save()

@csrf_exempt
def notifications_handler(request):
    data = JSONParser().parse(request)
    if not data:
        return HttpResponse(status=400)
    if data['job']['state'] == 'finished':
        encoding_id = data['job']['id']
        try:
            video_upload = Video.objects.get(encoding_id=encoding_id)
        except Video.DoesNotExist:
            return HttpResponse(status=201)

        handle_output(data['output'], video_upload)

    return HttpResponse(status=201)

def handle_output(output, video):
    # update the files
    if 'state' in output and output['state'] == 'finished':
        md5_checksum = output.get('md5_checksum', '')
        if md5_checksum is None:
            md5_checksum = ''
        output_video, created = OutputVideo.objects.get_or_create(base_video=video,
                                                                  output_id=output.get('id', 0),
                                                                  md5_checksum=md5_checksum)
        if not created and video_upload.encoding_complete:
            # we have already received this notification
            return False
        output_video.width = output.get('width', 0)
        output_video.height = output.get('height', 0)
        output_video.frame_rate = output.get('frame_rate', 0)
        output_video.duration_in_ms = output.get('duration_in_ms', 0)
        output_video.video_bitrate_in_kbps = output.get('video_bitrate_in_kbps', 0)
        output_video.audio_bitrate_in_kbps = output.get('audio_bitrate_in_kbps', 0)
        output_video.total_bitrate_in_kbps = output.get('total_bitrate_in_kbps', 0)
        output_video.video_codec = output.get('video_codec', 'None')
        output_video.format = output.get('format', 'None')
        output_video.audio_codec = output.get('audio_codec', 'None')
        output_video.size = output.get('file_size_in_bytes', 0)

        output_video.video = output['url']
        output_video.save()

        # save status
        video.encodings_generated = True
        video.save()


