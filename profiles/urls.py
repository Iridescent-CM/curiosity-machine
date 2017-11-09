from django.conf.urls import url, include
from profiles import views # deprecated
from .views import *

from curiositymachine.decorators import whitelist

urlpatterns = [
    url(r'^profiles/$', choose_profile, name="profiles"),
    url(r'^profile/edit/$', edit_profile, name="edit_profile"), url(r'^home/$', home, name="home"),

    ### urls below are deprecated

    url(r'^home/students/$', views.educator.students_dashboard, name='educator_dashboard_students'),
    url(r'^home/students/(?P<student_id>\d+)/$', views.educator.student_detail, name='educator_dashboard_student_detail'),
    url(r'^home/students/(?P<student_id>\d+)/challenge/(?P<challenge_id>\d+)/$', views.educator.conversation, name='educator_dashboard_progress_conversation'),
    url(r'^home/students/(?P<student_id>\d+)/password/$', views.educator.password_reset, name='educator_dashboard_student_password_reset'),
    url(r'^home/challenges/(?P<challenge_id>\d+)/$', views.educator.challenge_detail, name='educator_dashboard_challenge_detail'),
    url(r'^home/guides/$', views.educator.guides_dashboard, name='educator_dashboard_guides'),
    url(r'^data/progress_posts/$', whitelist('public')(views.educator.CommentList.as_view()), name='progress_graph_data'),
    url(r'^data/impact_survey/$', whitelist('public')(views.educator.ImpactSurveyView.as_view()), name='update_impact_survey'),
]
