from django.conf.urls import patterns, url, include

urlpatterns = patterns('challenges.views',
    url(r'^$', 'challenges', name='challenges'),
    url(r'^(?P<challenge_id>\d+)/$', 'challenge', name='challenge'),
    url(r'^(?P<challenge_id>\d+)/plan/$', 'plan_guest', name='plan_guest'),
    url(r'^(?P<challenge_id>\d+)/build/$', 'build_guest', name='build_guest'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/$', 'challenge_progress', name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/approve/$', 'challenge_progress_approve', name='challenge_progress_approve'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/(?P<stage>inspiration|plan|build)/$', 'challenge_progress', name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/(?P<stage>plan|build|test|reflect)/comments', include('cmcomments.urls', namespace='comments', app_name='comments')),
    url(r'^unclaimed/$', 'unclaimed_progresses', name='unclaimed_progresses'),
    url(r'^unclaimed/(?P<progress_id>\d+)$', 'claim_progress', name='claim_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/materials/$', 'change_materials', name='change_materials'),
    url(r'^(?P<challenge_id>\d+)/(?P<mode>favorite|unfavorite)$', 'set_favorite', name='set_favorite'),
    url(r'^favorite_challenges$', 'favorite_challenges', name='favorite_challenges'),
    url(r'^ajax_challenges$', 'ajax_challenges', name='ajax_challenges'),
    url(r'^filtered_challenges/(?P<filter_id>\d+)$', 'filtered_challenges', name='filtered_challenges'),
)
