from django.contrib import admin
from videos.models import Video, EncodedVideo

admin.site.register(Video)
admin.site.register(EncodedVideo)
