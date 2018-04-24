from django.conf import settings
from django.conf.urls import url
from .views import *

urlpatterns = [
    # keep these alive for students for now
    url(r'^connection/(?P<connection_id>\d+)/remove/$', remove_connection, name='remove_connection'),
    url(r'^connection/(?P<connection_id>\d+)/toggle/$', toggle_connection, name='toggle_connection'),
]

if settings.DEPRECATE_PARENT_ACCOUNTS:
    urlpatterns += [
        # deprecation intercept
        url(r'^.*/$', deprecated, name="deprecated"),
    ]

urlpatterns += [
    # old routes below, all superceded by the deprecation route above
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', home, name="home"),
    url(r'^connect/$', connect, name='connect'),
    url(r'^connection/(?P<connection_id>\d+)/$', view_child, name='view_child'),
]
