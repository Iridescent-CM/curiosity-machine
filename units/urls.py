from django.conf.urls import patterns, url
from units import views
from curiositymachine.decorators import whitelist

public = whitelist('public')

urlpatterns = patterns('units.views',
    url(r'^$', public(views.units), name='units'),
    url(r'^(?P<unit_id>\d+)/$', public(views.unit), name='unit'),
)
