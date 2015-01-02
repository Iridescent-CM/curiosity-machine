from django.core.management.base import BaseCommand, CommandError
import os, math
import boto
from boto.s3.connection import S3Connection

from django.conf import settings

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = settings.AWS_ERROR_STORAGE_BUCKET_NAME
CHUNK_SIZE = 52428800

APP_PATH = os.path.abspath(os.path.dirname(__file__) + '/../../')
SYSTEM_PATH = os.path.join(APP_PATH, 'static', 'system')

class Command(BaseCommand):
    
    def create_connection(self, access_key=AWS_ACCESS_KEY_ID, secret=AWS_SECRET_ACCESS_KEY):
        return S3Connection(access_key, secret)

    def create_bucket(self, connection, name=AWS_STORAGE_BUCKET_NAME):
        try:
            return connection.create_bucket(name)
        except boto.exception.S3CreateError:
            return connection.get_bucket(name)

    def upload_directory(self, bucket, base_path, recursive=False):
        upload_file_names = []
        for (path, dirs, files) in os.walk(base_path, followlinks=True):
            for filename in files:
                destpath = os.path.join(path.replace(base_path,''), filename)
                sourcepath = os.path.join(path, filename)

                k = boto.s3.key.Key(bucket)
                k.key = destpath
                if destpath in ["maintenance.html", "error.html"]:
                    print("Uploading {0}...".format(destpath))
                    print("URL: {0}\n".format(k.generate_url(expires_in=0, query_auth=False)))
                k.set_contents_from_filename(sourcepath)
                bucket.set_acl('public-read', destpath)
        
    def handle(self, *args, **options):
        connection = self.create_connection()
        bucket = self.create_bucket(connection)
        self.upload_directory(bucket, SYSTEM_PATH)
        bucket.set_acl('public-read') #set the bucket to be publicly-readable

