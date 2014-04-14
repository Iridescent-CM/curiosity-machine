from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
import profiles.urls

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='challenges/'), name='root'), # TODO: figure out how to use reverse() here without causing a circular import
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^videos/', include('videos.urls', namespace='videos', app_name='videos')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
)
