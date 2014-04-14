from django.db import models

class Video(models.Model):
    video = models.URLField(max_length=2083, null=True, blank=True)
    unique_hash = models.CharField(max_length=40)
    encoding_id = models.IntegerField(null=True, blank=True)
    encodings_generated = models.BooleanField(default=False)

class OutputVideo(models.Model):
    video = models.URLField(max_length=2083, null=True, blank=True)
    base_video = models.ForeignKey(Video, related_name='output_videos')
    md5_checksum = models.CharField(max_length=32, blank=True)
    output_id = models.IntegerField()
    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)
    frame_rate = models.IntegerField(default=0)
    duration_in_ms = models.IntegerField(default=0)
    video_codec = models.CharField(max_length=10, blank=True)
    format = models.CharField(max_length=10, blank=True)
    audio_codec = models.CharField(max_length=10, blank=True)
    size = models.IntegerField(default=0)
    video_bitrate_in_kbps = models.IntegerField(default=0)
    audio_bitrate_in_kbps = models.IntegerField(default=0)
    total_bitrate_in_kbps = models.IntegerField(default=0)
