from django.conf.urls import patterns, url
from profiles import views

from curiositymachine.decorators import whitelist

urlpatterns = patterns('profiles.views',
    url(r'^join/$', whitelist('public')(views.student.join), name='join'),
    url(r'^join/(?P<source>[^/]+)/$', whitelist('public')(views.student.join), name='join'),
    url(r'^join_as_mentor/$', whitelist('public')(views.mentor.join), name='join_as_mentor'),
    url(r'^join_as_mentor/(?P<source>[^/]+)/$', whitelist('public')(views.mentor.join), name='join_as_mentor'),
    url(r'^join_as_educator/$', whitelist('public')(views.educator.join), name='join_as_educator'),
    url(r'^join_as_educator/(?P<source>[^/]+)/$', whitelist('public')(views.educator.join), name='join_as_educator'),
    url(r'^join_as_parent/$', whitelist('public')(views.parent.join), name='join_as_parent'),
    url(r'^join_as_parent/(?P<source>[^/]+)/$', whitelist('public')(views.parent.join), name='join_as_parent'),
    url(r'^home/$', whitelist('unapproved_mentors')(views.dispatch), {'action': 'home'}, name='home'),
    url(r'^profile-edit/$', whitelist('unapproved_mentors')(views.dispatch), {'action': 'profile_edit'}, name='profile_edit'),
    url(r'^mentors/$', whitelist('public')(views.mentor.list_all), name='mentors'),
    url(r'^mentors/(?P<username>[^/]+)/$', whitelist('public')(views.mentor.show_profile), name='mentor_profile'),
    url(r'^underage/$', whitelist('underage')(views.student.underage), name='underage_student'),
    url(r'^unclaimed_progresses/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$', views.mentor.unclaimed_progresses, name='unclaimed_progresses'),
    url(r'^unclaimed_progresses/$', views.mentor.unclaimed_progresses, name='unclaimed_progresses'),
    url(r'^connect/$', views.parent.ParentConnectionCreateView.as_view(), name='connect'),
    url(r'^connection/(?P<connection_id>\d+)/$', views.parent.ChildDetailView.as_view(), name='connection'),
    url(r'^connection/(?P<connection_id>\d+)/remove/$', views.dispatch, {'action': 'remove_connection'}, name='remove_connection'),
    url(r'^connection/(?P<connection_id>\d+)/toggle/$', views.student.ParentConnectionToggleView.as_view(), name='toggle_connection'),
)
