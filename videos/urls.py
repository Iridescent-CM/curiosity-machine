from django.conf.urls import patterns, url

urlpatterns = patterns('cmcomments.views',
    url(r'^$', 'comments', name='comments'),
    url(r'^(?P<format>(video|picture))/$', 'comments', name='comments'),
    url(r'^zencoder/notifications_handler/$', 'notifications_handler', name='notifications_handler'),
)
