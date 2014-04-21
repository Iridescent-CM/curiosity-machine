from django.db import models
from django.conf import settings
from .tasks import upload_filepicker_image
import django_rq

class Image(models.Model):
    filepicker_url = models.TextField(blank=True) # originally uploaded as this
    md5_hash = models.CharField(max_length=32, blank=True)
    filename = models.CharField(max_length=1024, blank=True)

    @property
    def url(self):
        if self.filename:
            return "{base}/{bucket}/{key}".format(base=settings.S3_URL_BASE, bucket=settings.AWS_STORAGE_BUCKET_NAME, key=self.filename)
        else:
            return self.filepicker_url

    @classmethod
    def from_filepicker_with_job(cls, filepicker_url):
        image = cls.objects.create(filepicker_url=filepicker_url)
        django_rq.enqueue(upload_filepicker_image, image)
        return image
