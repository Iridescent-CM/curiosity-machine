import tinys3
import requests
import tempfile
import hashlib
import django_rq
from django.conf import settings


def sum_for_fd(fd):
    md5 = hashlib.md5()
    for chunk in iter(lambda: fd.read(128 * md5.block_size), b''):
        md5.update(chunk)
    return md5.hexdigest()

def upload_to_s3(obj, key_prefix='', queue_after=None): # key_prefix should include the trailing / if necessary
    response = requests.get(obj.source_url, stream=True)
    conn = tinys3.Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY, tls=True)

    with tempfile.TemporaryFile() as fd:
        for chunk in response.iter_content(1024*1024): # write with 1MB chunks -- not sure if there is any significant performance impact here though
            fd.write(chunk)
        fd.seek(0) # reset to beginning of file for reading
        obj.md5_hash = sum_for_fd(fd) # get md5 hash and write to model
        fd.seek(0) # reset again, this time to prepare to upload
        key = key_prefix + obj.md5_hash
        conn.upload(key, fd, settings.AWS_STORAGE_BUCKET_NAME, public=True) # upload to AWS_STORAGE_BUCKET_NAME with the hash as the key
        obj.key = key # now that it's uploaded, set the filename to the model too

    obj.save()

    if queue_after:
        django_rq.enqueue(queue_after, obj)

def email_inactive_users():
    from profiles.models import Profile
    profiles = Profile.inactive_students()
    for profile in profiles:
        profile.deliver_inactive_email()