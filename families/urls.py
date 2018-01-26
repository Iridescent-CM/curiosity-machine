from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^convert/$', convert, name="convert"),
    url(r'^home/$', home, name="home"),
    url(r'^stage-1/$', stage_1, name="stage_1"),
    url(r'^stage-2/$', stage_2, name="stage_2"),
]