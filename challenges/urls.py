from django.conf.urls import patterns, url, include
from curiositymachine.decorators import whitelist
from challenges import views

public = whitelist('public')
defer = whitelist('maybe_public')

urlpatterns = patterns('challenges.views',
    url(r'^$', public(views.challenges), name='challenges'),
    url(r'^(?P<challenge_id>\d+)/$', public(views.InspirationPreviewDispatch.as_view()), name='preview_inspiration'),
    url(r'^(?P<challenge_id>\d+)/landing/$', defer(views.LandingView.as_view()), name='preview_landing'),
    url(r'^(?P<challenge_id>\d+)/examples/$', defer(views.ExamplesView.as_view()), name='examples'),
    url(r'^(?P<challenge_id>\d+)/examples/delete/$', views.ExamplesDeleteView.as_view(), name='delete_example'),
    url(r'^(?P<challenge_id>\d+)/plan/$', defer(views.preview_plan), name='preview_plan'),
    url(r'^(?P<challenge_id>\d+)/build/$', defer(views.preview_build), name='preview_build'),
    url(r'^(?P<challenge_id>\d+)/reflect/$', defer(views.preview_reflect), name='preview_reflect'),
    url(r'^(?P<challenge_id>\d+)/start/$', 'start_building', name='start_building'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/$', 'redirect_to_stage', name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/inspiration/$', views.InspirationProgressDispatch.as_view(), name='inspiration_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/(?P<stage>plan|build|test|reflect)/$', 'challenge_progress', name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/(?P<stage>plan|build|test|reflect)/comments/', include('cmcomments.urls', namespace='comments', app_name='comments')),
    url(r'^unclaimed/$', 'unclaimed_progresses', name='unclaimed_progresses'),
    url(r'^unclaimed/(?P<progress_id>\d+)$', 'claim_progress', name='claim_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/materials/$', 'change_materials', name='change_materials'),
    url(r'^(?P<challenge_id>\d+)/(?P<mode>favorite|unfavorite)$', 'set_favorite', name='set_favorite'),
    url(r'^favorite_challenges$', 'favorite_challenges', name='favorite_challenges'),
)
