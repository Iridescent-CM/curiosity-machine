from django.conf.urls import patterns, url

urlpatterns = patterns('challenges.views',
    url(r'^$', 'challenges', name='challenges'),
    url(r'^(?P<challenge_id>\d+)/$', 'challenge', name='challenge'),
)
