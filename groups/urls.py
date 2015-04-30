from django.conf.urls import patterns, url
from groups import views

urlpatterns = patterns('groups.views',
    url(r'^create$', views.GroupCreateView.as_view(), name='create'),
    url(r'^join_group$', 'join_group', name='join_group'),
    url(r'^accept_invitation/(?P<group_id>\d+)/$', 'accept_invitation', name='accept_invitation'),
    url(r'^(?P<group_id>\d+)/$', views.GroupDetailView.as_view(), name='group'),
    url(r'^(?P<group_id>\d+)/edit$', views.GroupEditView.as_view(), name='edit'),
    url(r'^(?P<group_id>\d+)/delete$', views.GroupDeleteView.as_view(), name='delete'),
    url(r'^(?P<group_id>\d+)/leave$', views.GroupLeaveView.as_view(), name='leave'),
    url(r'^(?P<group_id>\d+)/invite/$', views.InvitationCreateView.as_view(), name='invite_to_group'),
    url(r'^(?P<group_id>\d+)/invitation/$', views.UpdateInvitationsView.as_view(), name='manage_invitations'),
    url(r'^(?P<group_id>\d+)/invitation/reject$', views.InvitationRejectView.as_view(), name='reject_invitation'),
    url(r'^(?P<group_id>\d+)/member/$', views.UpdateMembersView.as_view(), name='manage_members'),
    url(r'^(?P<group_id>\d+)/member/(?P<user_id>[\w.@+-]+)/$', views.GroupMemberDetailView.as_view(), name='member'),
)
