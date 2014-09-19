from django.conf.urls import patterns, url

urlpatterns = patterns('training.views',
    url(r'^(?P<module_order>\d+)/$', 'module', name='module'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/$', 'task', name='task'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/comments/$', 'comments', name='comments'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/comments/(?P<thread_id>\d+)$', 'comments', name='comments'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/comments/(?P<username>[\w.@+-]+)$', 'approve_task_progress', name='approve_task_progress'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/(?P<thread_id>\d+)/starter$', 'thread_starter', name='thread_starter'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/(?P<thread_id>\d+)/replies$', 'replies', name='replies'),
)
