from django.conf.urls import patterns, url

urlpatterns = patterns('profiles.views',
    url(r'^join/$', 'join', name='join'),
    url(r'^home/$', 'home', name='home'),
    url(r'^profile-edit/$', 'profile_edit', name='profile_edit'),
    url(r'^students/(?P<username>[^/]+)/$', 'profile_details', {'mentor': False}, name='student_profile_details'),
    url(r'^mentors/(?P<username>[^/]+)/$', 'profile_details', {'mentor': True}, name='mentor_profile_details'),
)
