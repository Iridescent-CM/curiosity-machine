from curiositymachine.decorators import whitelist
from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^profile/new/$', create, name="create_profile"),
    url(r'^profile/edit/$', edit, name="edit_profile"),
    url(r'^home/$', home, name="home"),
    url(r'^home/mychallenges/$', my_challenges, name="my_challenges"),
    url(r'^home/membership/(?P<membership_id>\d+)/$', membership_challenges, name="membership"),
    url(r'^home/favorites/$', favorites, name="favorites"),
    url(r'^home/activity/$', activity, name='activity'),
    url(r'^unapproved/$', whitelist('unapproved_students')(unapproved), name='unapproved'),
]