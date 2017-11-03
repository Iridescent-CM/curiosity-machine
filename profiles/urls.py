from django.conf.urls import url, include
from profiles import views # deprecated
from .views import *

from curiositymachine.decorators import whitelist

urlpatterns = [
    url(r'^profiles/$', choose_profile, name="profiles"),
    url(r'^home/$', home, name="home"),

    ### urls below are deprecated

    url(r'^join/$', whitelist('public')(views.student.join), name='join'),
    url(r'^join/(?P<source>[^/]+)/$', whitelist('public')(views.student.join), name='join'),
    url(r'^join_as_mentor/$', whitelist('public')(views.mentor.join), name='join_as_mentor'),
    url(r'^join_as_mentor/(?P<source>[^/]+)/$', whitelist('public')(views.mentor.join), name='join_as_mentor'),
    url(r'^join_as_educator/$', whitelist('public')(views.educator.join), name='join_as_educator'),
    url(r'^join_as_educator/(?P<source>[^/]+)/$', whitelist('public')(views.educator.join), name='join_as_educator'),
    url(r'^join_as_parent/$', whitelist('public')(views.parent.join), name='join_as_parent'),
    url(r'^join_as_parent/(?P<source>[^/]+)/$', whitelist('public')(views.parent.join), name='join_as_parent'),
    #url(r'^home/$', whitelist('unapproved_mentors')(views.dispatch), {'action': 'home'}, name='home'),
    url(r'^home/students/$', views.educator.students_dashboard, name='educator_dashboard_students'),
    url(r'^home/students/(?P<student_id>\d+)/$', views.educator.student_detail, name='educator_dashboard_student_detail'),
    url(r'^home/students/(?P<student_id>\d+)/challenge/(?P<challenge_id>\d+)/$', views.educator.conversation, name='educator_dashboard_progress_conversation'),
    url(r'^home/students/(?P<student_id>\d+)/password/$', views.educator.password_reset, name='educator_dashboard_student_password_reset'),
    url(r'^home/challenges/(?P<challenge_id>\d+)/$', views.educator.challenge_detail, name='educator_dashboard_challenge_detail'),
    url(r'^home/guides/$', views.educator.guides_dashboard, name='educator_dashboard_guides'),
    url(r'^data/progress_posts/$', whitelist('public')(views.educator.CommentList.as_view()), name='progress_graph_data'),
    url(r'^data/impact_survey/$', whitelist('public')(views.educator.ImpactSurveyView.as_view()), name='update_impact_survey'),
    url(r'^profile-edit/$', whitelist('unapproved_mentors')(views.dispatch), {'action': 'profile_edit'}, name='profile_edit'),
    url(r'^mentors/$', whitelist('public')(views.mentor.list_all), name='mentors'),
    url(r'^mentors/(?P<username>[^/]+)/$', whitelist('public')(views.mentor.show_profile), name='mentor_profile'),
    url(r'^underage/$', whitelist('underage')(views.student.underage), name='underage_student'),
    url(r'^unclaimed_progresses/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$', views.mentor.unclaimed_progresses, name='unclaimed_progresses'),
    url(r'^unclaimed_progresses/$', views.mentor.unclaimed_progresses, name='unclaimed_progresses_base'),
    url(r'^claimed_progresses/$', views.mentor.claimed_progresses, name='claimed_progresses'),
    url(r'^connect/$', views.parent.ParentConnectionCreateView.as_view(), name='connect'),
    url(r'^connection/(?P<connection_id>\d+)/$', views.parent.ChildDetailView.as_view(), name='connection'),
    url(r'^connection/(?P<connection_id>\d+)/remove/$', views.dispatch, {'action': 'remove_connection'}, name='remove_connection'),
    url(r'^connection/(?P<connection_id>\d+)/toggle/$', views.student.ParentConnectionToggleView.as_view(), name='toggle_connection'),
]
