from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', home, name="home"),
]
