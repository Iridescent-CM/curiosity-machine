from django.conf.urls import patterns, url
from units import views

urlpatterns = patterns('units.views',
    url(r'^$', views.units, name='units'),
    url(r'^(?P<unit_id>\d+)/$', views.unit, name='unit'),
)
