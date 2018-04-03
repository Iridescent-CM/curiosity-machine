from curiositymachine.decorators import whitelist
from django.conf.urls import url, include
from .views import *

public = whitelist('public')
urlpatterns = [
    url(r'^hooks/status/$', public(status_hook), name="status_hook"),
    url(r'^(?P<survey_pk>[^/]+)/complete/$', complete, name="survey_complete"),
]