from django.conf.urls import patterns, url

urlpatterns = patterns('units.views',
    url(r'^$', 'units', name='units'),
    url(r'^(?P<unit_id>\d+)/$', 'unit', name='unit'),
)
