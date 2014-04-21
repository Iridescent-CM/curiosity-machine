import tinys3
import requests
import tempfile
import hashlib
from django.conf import settings

def upload_filepicker_image(image):
    response = requests.get(image.filepicker_url)
    conn = tinys3.Connection(settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)

    with tempfile.TemporaryFile() as fd:
        for chunk in response.iter_content(256*1024): # write with 256KiB chunks -- not sure if there is any real performance impact here though
            fd.write(chunk)
        fd.seek(0) # reset to beginning of file for reading
        image.md5_hash = hashlib.md5(fd.read()).hexdigest() # get md5 hash and write to model
        fd.seek(0) # reset again, this time to prepare to upload
        key = image.md5_hash
        conn.upload(key, fd, settings.AWS_STORAGE_BUCKET_NAME) # upload to AWS_STORAGE_BUCKET_NAME with the hash as the key
        conn.update_metadata(key, bucket=settings.AWS_STORAGE_BUCKET_NAME, public=True) # make the file public
        image.filename = key # now that it's uploaded, set the filename to the model too

    image.save()
