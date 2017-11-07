from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', home, name="home"),
    url(r'^connect/$', connect, name='connect'),
    url(r'^connection/(?P<connection_id>\d+)/$', view_child, name='view_child'),
    url(r'^connection/(?P<connection_id>\d+)/remove/$', remove_connection, name='remove_connection'),
    url(r'^connection/(?P<connection_id>\d+)/toggle/$', toggle_connection, name='toggle_connection'),
]
