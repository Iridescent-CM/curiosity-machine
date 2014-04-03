from django.conf.urls import patterns, url, include

urlpatterns = patterns('challenges.views',
    url(r'^$', 'challenges', name='challenges'),
    url(r'^(?P<challenge_id>\d+)/$', 'challenge', name='challenge'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/$', 'challenge_progress', name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/comments/', include('cmcomments.urls', namespace='comments', app_name='comments')),
)
