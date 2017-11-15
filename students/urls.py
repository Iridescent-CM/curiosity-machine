from curiositymachine.decorators import whitelist
from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', home, name="home"),
    url(r'^underage/$', whitelist('underage')(underage), name='underage'),
]