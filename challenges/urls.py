from django.conf.urls import url, include
from curiositymachine.decorators import whitelist
from challenges import views

public = whitelist('public')

app_name = "challenges"

urlpatterns = [
    url(r'^$', public(views.challenges), name='challenges'),
    url(r'^(?P<challenge_id>\d+)/$', public(views.InspirationPreviewDispatch.as_view()), name='preview_inspiration'),
    url(r'^(?P<challenge_id>\d+)/examples/$', views.ExamplesView.as_view(), name='examples'),
    url(r'^(?P<challenge_id>\d+)/examples/delete/$', views.ExamplesDeleteView.as_view(), name='delete_example'),
    url(r'^(?P<challenge_id>\d+)/plan/$', views.preview_stage, {"stage": "plan"}, name='preview_plan'),
    url(r'^(?P<challenge_id>\d+)/build/$', views.preview_stage, {"stage": "build"}, name='preview_build'),
    url(r'^(?P<challenge_id>\d+)/reflect/$', views.preview_stage, {"stage": "reflect"}, name='preview_reflect'),
    url(r'^(?P<challenge_id>\d+)/start/$', views.start_building, name='start_building'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/$', views.redirect_to_stage, name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/inspiration/$', views.InspirationProgressDispatch.as_view(), name='inspiration_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/(?P<stage>plan|build|test|reflect)/$', views.challenge_progress, name='challenge_progress'),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/(?P<stage>plan|build|test|reflect)/comments/', include('cmcomments.urls')),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/(?P<stage>plan|build|test|reflect)/quiz/', include('quizzes.urls')),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/feedback/', include('feedback.urls')),
    url(r'^(?P<challenge_id>\d+)/(?P<username>[^/]+)/materials/$', views.change_materials, name='change_materials'),
    url(r'^(?P<challenge_id>\d+)/(?P<mode>favorite|unfavorite)$', views.set_favorite, name='set_favorite'),
    url(r'^favorite_challenges$', views.favorite_challenges, name='favorite_challenges'),
]
