from curiositymachine.decorators import whitelist
from django.conf.urls import url, include
from .views import *

public = whitelist('public')

app_name = "surveys"

urlpatterns = [
    url(r'^hooks/status/$', public(status_hook), name="status_hook"),
    url(r'^([^/]+/)?completed/$', completed, name="survey_completed"), # used to take survey_pk as part of url
]