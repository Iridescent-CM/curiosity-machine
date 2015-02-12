from django.conf.urls import patterns, url

urlpatterns = patterns('groups.views',
    url(r'^$', 'groups', name='groups'),
    url(r'^(?P<group_id>\d+)/$', 'group', name='group'),
)
