from django.conf.urls import url
from units import views

urlpatterns = [
    url(r'^$', views.units, name='units'),
    url(r'^(?P<unit_id>\d+)/$', views.unit, name='unit'),
    url(r'^(?P<slug>\w+)/$', views.unit, name='unit_by_slug'),
]
