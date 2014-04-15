from django.conf.urls import patterns, url

urlpatterns = patterns('videos.views',
    url(r'^zencoder/notifications_handler/$', 'notifications_handler', name='notifications_handler'),
)
