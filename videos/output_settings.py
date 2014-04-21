from django.conf import settings
from django.core.urlresolvers import reverse
'''
Recomendations from https://app.zencoder.com/docs/guides/encoding-settings
'''
NOTIFICATIONS = [
    {
      "url": settings.ZENCODER_NOTIFICATIONS_URL,
      "format": "json"
    }
]

STANDARD_HD = {
# Plays on:
#  iOS: iPhone 4, iPad, Apple TV*, newer iPod Touch
#  Android: Nexus One, Droid, maybe others. (YMMV on these, though. Some users report trouble with 720p video.)
#  Other: PS3, web
# Doesn't play on:
#  iOS: iPod 5G/5.5G/Classic, iPhone 3GS and before, older iPod Touch PSP, old Apple TV*
#  Blackberry: all
#  Android: others
#  Other: PSP, PS3, Xbox 360, web
    "url": ".mp4",
    "audio_bitrate": 160,
    "audio_sample_rate": 48000,
    "height": 720,
    "width": 1280,
    "max_frame_rate": 30,
    "video_bitrate": 5000,
    "h264_profile": "main",
    "h264_level": 3.1,
    "public": True,
    "notifications": NOTIFICATIONS,
    "thumbnails": {
        "format": "jpg",
        "number": 4,
        "width": 1216,
        "height": 684,
        "base_url": "s3://%s" % settings.ZENCODER_S3_BUCKET,
        "public": True,
    },
}

OUTPUTS = [STANDARD_HD,]
    # {
    # # Plays on:
    # #  iOS: iPhone, iPad, Apple TV, iPod Touch, iPod Classic, iPod 5.5G
    # #  Blackberry: Bold 9000, Curve 8910, 8900, 8520, Pearl 9XXX, Storm, Storm 2, Torch, Tour, Bold 9650 + 9700
    # #  Android: All (?)
    # # Other: PSP (3.30+), PS3, Xbox 360, web, Palm Pre*
    # #  Doesn't play on:
    # #  iPod 5G, PSP (pre-3.30), Blackberry Curve 9330, 9300, 8530, 83XX, Pearl 8XXX, 88XX
    #   "url": ".mp4",
    #   "audio_bitrate": 128,
    #   "audio_sample_rate": 44100,
    #   "height": 480,
    #   "width": 640,
    #   "max_frame_rate": 30,
    #   "video_bitrate": 1500,
    #   "h264_level": 3
    # },
    # {
    # Plays on:
    #  iOS: iPhone, iPad, Apple TV, iPod Touch, iPod Classic, iPod 5.5G
    #  Blackberry: Bold 9000, Curve 8910, 8900, 8520, Pearl 9XXX, Storm, Storm 2, Torch, Tour, Bold 9650 + 9700
    #  Android: All (?)
    #  Other: PSP (3.30+), PS3, Xbox 360, web, Palm Pre*
    # Doesn't play on:
    #  iPod 5G, PSP (pre-3.30), Blackberry Curve 9330, 9300, 8530, 83XX, Pearl 8XXX, 88XX
    #   "url": ".mp4",
    #   "audio_bitrate": 128,
    #   "audio_sample_rate": 44100,
    #   "height": 480,
    #   "width": 640,
    #   "max_frame_rate": 30,
    #   "video_bitrate": 1500,
    #   "h264_level": 3
    # },