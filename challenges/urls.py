from django.conf.urls import patterns, url

urlpatterns = patterns('challenges.views',
    url(r'^(?P<challenge_id>\d+)/inspiration/$', 'challenge_inspiration', name='challenge_inspiration'),
    url(r'^(?P<challenge_id>\d+)/plan/$', 'challenge_plan', name='challenge_plan'),
    url(r'^(?P<challenge_id>\d+)/build/$', 'challenge_build', name='challenge_build'),
    url(r'^(?P<challenge_id>\d+)/reflect/$', 'challenge_reflect', name='challenge_reflect'),
)
