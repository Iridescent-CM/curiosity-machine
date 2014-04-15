import os
import logging
import argparse


os.environ['DJANGO_SETTINGS_MODULE'] = 'curiositymachine.settings'

import django
django.setup()

from django.conf import settings

from zencoder import Zencoder
from videos.models import Video, OutputVideo
from videos.views import handle_output

logger = logging.getLogger(__name__)

class VideoAdmin(object):

    DO_ALL = -1

    def __init__(self, count):
        self.count = count
        self.client = Zencoder(settings.ZENCODER_API_KEY)

    '''
    looks for video upload jobs that have finished but have not sent a notification to our system
    '''
    def update_encoding_outputs(self):
        updated_count = 0
        vups = Video.objects.filter(encodings_generated=False)
        print('videos that need encodedings: %s' % vups.count())
        for vu in vups:
            if not vu.encoding_id:
                print('Error: video encodeding job id is blank')
                continue
            print('video absolute url: %s' % vu.video)
            print('encoding job id: %s' % vu.encoding_id)
            try:
                details = self.client.job.details(vu.encoding_id)
            except:
                print('Error: connection error with zencoder')
                continue
            data = details.body
            if 'job' in data and 'output_media_files' in data['job']:
                output_media_files = data['job']['output_media_files']
                for media_file in output_media_files:
                    # look up output file
                    output_id = media_file['id']
                    try:
                        output_details = self.client.output.details(output_id)
                    except:
                        print('Error: connection error with zencoder')
                    data = output_details.body
                    if 'state' in data and data['state'] == 'finished':
                        # update data with completed output file
                        print('trying to updated output: %s' % output_id)
                        handle_output(data, vu)
                        print('successfully updated output: %s' % output_id)

            if self.count != self.DO_ALL:
                updated_count += 1
                if updated_count >= self.count:
                    break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Admin script for videos')
    parser.add_argument('--count', dest='count', action='store', default=VideoAdmin.DO_ALL,type=int,
                        help='number of video encodings to update')
    args = parser.parse_args()

    va = VideoAdmin(args.count)
    va.update_encoding_outputs()
