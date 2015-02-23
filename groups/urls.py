from django.conf.urls import patterns, url

urlpatterns = patterns('groups.views',
    url(r'^$', 'groups', name='groups'),
    url(r'^join_group$', 'join_group', name='join_group'),
    url(r'^leave_group$', 'leave_group', name='leave_group'),
    url(r'^(?P<group_id>\d+)/$', 'group', name='group'),
)
