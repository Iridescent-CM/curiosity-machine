from django.conf.urls import url, include
from profiles import views # deprecated
from .views import *

from curiositymachine.decorators import whitelist

app_name = "profiles"

urlpatterns = [
    url(r'^profiles/$', choose_profile, name="profiles"),
    url(r'^profile/edit/$', whitelist('unapproved_family')(edit_profile), name="edit_profile"),
    url(r'^home/$', home, name="home"),
]
