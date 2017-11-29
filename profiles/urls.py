from django.conf.urls import url, include
from profiles import views # deprecated
from .views import *

from curiositymachine.decorators import whitelist

urlpatterns = [
    url(r'^profiles/$', choose_profile, name="profiles"),
    url(r'^profile/edit/$', whitelist('unapproved_mentors')(edit_profile), name="edit_profile"),
    url(r'^home/$', whitelist('unapproved_mentors')(home), name="home"),
]
