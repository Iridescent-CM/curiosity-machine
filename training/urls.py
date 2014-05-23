from django.conf.urls import patterns, url

urlpatterns = patterns('training.views',
    url(r'^(?P<module_id>\d+)/$', 'module', name='module'),
    url(r'^(?P<module_id>\d+)/comments/$', 'comments', name='comments'),
    url(r'^(?P<module_id>\d+)/comments/(?P<thread_id>\d+)$', 'comments', name='comments'),
    url(r'^(?P<module_id>\d+)/comments/(?P<username>[\w.@+-]+)$', 'approve_module_progress', name='approve_module_progress'),
)
