from django.conf.urls import patterns, url
from groups import views

urlpatterns = patterns('groups.views',
    url(r'^$', views.GroupListView.as_view(), name='groups'),
    url(r'^create$', views.GroupCreateView.as_view(), name='create'),
    url(r'^join_group$', 'join_group', name='join_group'),
    url(r'^leave_group$', 'leave_group', name='leave_group'),
    url(r'^accept_invitation/(?P<group_id>\d+)/$', 'accept_invitation', name='accept_invitation'),
    url(r'^(?P<group_id>\d+)/invite/$', views.InvitationCreateView.as_view(), name='invite_to_group'),
    url(r'^(?P<group_id>\d+)/$', views.GroupDetailView.as_view(), name='group')
)
