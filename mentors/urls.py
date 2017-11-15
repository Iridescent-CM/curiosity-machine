from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', home, name="home"),
    url(r'^community/$', list_all, name="list"),
    url(r'^community/(?P<username>[^/]+)/$', public_profile, name='public_profile'),
    url(r'^claimed/$', claimed, name='claimed_progresses'),
    url(r'^unclaimed/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$', unclaimed_by_date, name='unclaimed_progresses'),
    url(r'^unclaimed/$', unclaimed_by_source, name='unclaimed_progresses_base'),
]
