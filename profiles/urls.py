from django.conf.urls import patterns, url

urlpatterns = patterns('profiles.views',
    url(r'^join/$', 'join', name='join'),
    url(r'^home/$', 'home', name='home'),
    url(r'^profile-edit/$', 'profile_edit', name='profile_edit'),
    url(r'^students/(?P<username>[^/]+)/$', 'student_profile_details', name='student_profile_details'),
    url(r'^mentors/(?P<username>[^/]+)/$', 'mentor_profile_details', name='mentor_profile_details'),
)
