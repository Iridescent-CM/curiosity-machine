from django.db import models
from django.conf import settings
from curiositymachine.tasks import upload_to_s3
import django_rq

class Video(models.Model):
    source_url = models.URLField(max_length=2048, blank=True)
    md5_hash = models.CharField(max_length=32, blank=True) # this is the hash of the ORIGINAL file, not the encoded file
    key = models.CharField(max_length=1024, blank=True) # this is the filename of the ORIGINAL file, not the encoded file

    @property
    def url(self):
        if self.key:
            return "{base}/{bucket}/{key}".format(base=settings.S3_URL_BASE, bucket=settings.AWS_STORAGE_BUCKET_NAME, key=self.key)
        else:
            return self.source_url

    @classmethod
    def from_filepicker_with_job(cls, source_url):
        from .tasks import encode_video
        video = cls.objects.create(source_url=source_url)
        django_rq.enqueue(upload_to_s3, video, key_prefix="videos/", queue_after=encode_video)
        return video

class EncodedVideo(models.Model):
    video = models.ForeignKey(Video, related_name="encoded_videos")
    key = models.CharField(max_length=1024)
    width = models.IntegerField()
    height = models.IntegerField()
    mime_type = models.CharField(max_length=255) # generally video/mp4, video/webm or video/ogg
    raw_encoding_details = models.TextField()

    @property
    def url(self):
        return "{base}/{bucket}/{key}".format(base=settings.S3_URL_BASE, bucket=settings.AWS_STORAGE_BUCKET_NAME, key=self.key)
