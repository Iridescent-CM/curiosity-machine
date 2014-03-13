from django.conf.urls import patterns, url

urlpatterns = patterns('profiles.views',
    url(r'^students/(?P<email>[^/]+)/$', 'profile_details', name='profile_details'),
    url(r'^mentors/(?P<email>[^/]+)/$', 'profile_details', name='profile_details_mentors'),
)
