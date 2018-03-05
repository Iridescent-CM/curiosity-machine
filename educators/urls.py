from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', challenges, name="home"),
    url(r'^home/challenges/(?P<challenge_id>\d+)/$', challenge, name='challenge'),
    url(r'^home/students/$', students, name='students'),
    url(r'^home/students/(?P<student_id>\d+)/$', student, name='student'),
    url(r'^home/students/(?P<student_id>\d+)/password/$', student_password_reset, name='student_password_reset'),
    url(r'^home/students/(?P<student_id>\d+)/challenge/(?P<challenge_id>\d+)/$', conversation, name='conversation'),
    url(r'^home/guides/$', guides, name='guides'),
    url(r'^data/impact_survey/$', impact_data, name='update_impact_survey'),
    url(r'^data/progress_posts/$', comments, name='progress_graph_data'),
    url(r'^coach/$', coach, name='create_coach'),
    url(r'^coach-conversion/$', coach_conversion, name="coach_conversion"),
]
