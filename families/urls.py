from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^email/edit/$', edit_email, name="edit_email"),
    url(r'^conversion/$', conversion, name="conversion"),
    url(r'^home/$', home, name="home"),
    url(r'^activity/$', activity, name='activity'),
    url(r'^stage-1/$', stage_1, name="stage_1"),
    url(r'^stage-2/$', stage_2, name="stage_2"),
]

if settings.DEBUG:
    urlpatterns += [
        url(r'^interruption/prereq/$', prereq_interruption),
        url(r'^interruption/postsurvey/$', postsurvey_interruption),
    ]