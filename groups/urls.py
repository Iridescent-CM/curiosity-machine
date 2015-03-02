from django.conf.urls import patterns, url

urlpatterns = patterns('groups.views',
    url(r'^$', 'groups', name='groups'),
    url(r'^create$', 'create', name='create'),
    url(r'^join_group$', 'join_group', name='join_group'),
    url(r'^leave_group$', 'leave_group', name='leave_group'),
    url(r'^accept_invitation/(?P<group_id>\d+)/(?P<token>\w+)$', 'accept_invitation', name='accept_invitation'),
    url(r'^invite_to_group/(?P<group_id>\d+)$', 'invite_to_group', name='invite_to_group'),
    url(r'^(?P<group_id>\d+)/$', 'group', name='group'),
)
