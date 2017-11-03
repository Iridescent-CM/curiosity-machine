from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/(?P<id>\d+)/edit', edit, name="edit_profile"),
]