from django.conf.urls import patterns, url
from training import views
from curiositymachine.decorators import whitelist

wrap = whitelist('unapproved_mentors')

urlpatterns = patterns('training.views',
    url(r'^(?P<module_order>\d+)/$', wrap(views.module), name='module'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/$', wrap(views.task), name='task'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/comments/$', wrap(views.comments), name='comments'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/comments/(?P<thread_id>\d+)$', wrap(views.comments), name='comments'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/comments/(?P<username>[\w.@+-]+)$', wrap(views.approve_task_progress), name='approve_task_progress'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/(?P<thread_id>\d+)/starter$', wrap(views.thread_starter), name='thread_starter'),
    url(r'^(?P<module_order>\d+)/(?P<task_order>\d+)/(?P<thread_id>\d+)/replies$', wrap(views.replies), name='replies'),
)
