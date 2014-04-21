from django.db import models
from django.conf import settings
from curiositymachine.tasks import upload_to_s3
import django_rq

class Image(models.Model):
    source_url = models.URLField(max_length=2048, blank=True)
    md5_hash = models.CharField(max_length=32, blank=True)
    key = models.CharField(max_length=1024, blank=True)

    @property
    def url(self):
        if self.key:
            return "{base}/{bucket}/{key}".format(base=settings.S3_URL_BASE, bucket=settings.AWS_STORAGE_BUCKET_NAME, key=self.key)
        else:
            return self.source_url

    @classmethod
    def from_filepicker_with_job(cls, source_url):
        image = cls.objects.create(source_url=source_url)
        django_rq.enqueue(upload_to_s3, image, key_prefix='images/')
        return image
