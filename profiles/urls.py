from django.conf.urls import patterns, url

urlpatterns = patterns('profiles.views',
    url(r'^join/$', 'join', name='join'),
    url(r'^join_as_mentor/$', 'join_as_mentor', name='join_as_mentor'),
    url(r'^home/$', 'home', name='home'),
    url(r'^profile-edit/$', 'profile_edit', name='profile_edit'),
    url(r'^mentors/$', 'mentors', name='mentors'),
    url(r'^mentors/(?P<username>[^/]+)/$', 'mentor_profile', name='mentor_profile'),
    url(r'^underage/$', 'underage_student', name='underage_student'),
)
