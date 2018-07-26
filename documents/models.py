from django.db import models
from django.conf import settings
from curiositymachine.tasks import upload_to_s3
import django_rq
import logging

logger = logging.getLogger(__name__)

class Document(models.Model):
    source_url = models.URLField(max_length=2048, blank=True)
    md5_hash = models.CharField(max_length=32, blank=True)
    key = models.CharField(max_length=1024, blank=True)
    filename = models.CharField(max_length=2048, blank=True)

    @property
    def url(self):
        if self.key:
            return "{base}/{bucket}/{key}".format(base=settings.S3_URL_BASE, bucket=settings.AWS_STORAGE_BUCKET_NAME, key=self.key)
        else:
            return self.source_url

    @classmethod
    def from_source_with_job(cls, source_url, filename):
        if not source_url:
            logger.warn("No source url provided for Document", stack_info=True)
            return None
        doc = cls.objects.create(source_url=source_url, filename=filename)
        doc.fetch_from_source()
        return doc

    def fetch_from_source(self):
        if not self.key:
           django_rq.enqueue(upload_to_s3, self, key_prefix='documents/')

    def __str__(self):
        return "Document: id={}, url={}".format(self.id, self.url)