from django.conf.urls import patterns, url

urlpatterns = patterns('training.views',
    url(r'^(?P<module_id>\d+)/$', 'module', name='module'),
    url(r'^(?P<module_id>\d+)/comments/$', 'comments', name='comments'),
)
