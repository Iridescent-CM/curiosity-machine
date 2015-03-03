from django.conf.urls import patterns, url
from profiles import views


urlpatterns = patterns('profiles.views',
    url(r'^join/$', views.student.join, name='join'),
    url(r'^join_as_mentor/$', views.mentor.join, name='join_as_mentor'),
    url(r'^join_as_educator/$', views.educator.join, name='join_as_educator'),
    url(r'^home/$', views.dispatch, {'action': 'home'}, name='home'),
    url(r'^profile-edit/$', views.dispatch, {'action': 'profile_edit'}, name='profile_edit'),
    url(r'^mentors/$', views.mentor.list_all, name='mentors'),
    url(r'^mentors/(?P<username>[^/]+)/$', views.mentor.show_profile, name='mentor_profile'),
    url(r'^underage/$', views.student.underage, name='underage_student'),
    url(r'^consent_form/(?P<token>\w+)/$', views.student.consent_form, name='consent_form'),
    url(r'^resend_consent_form_email/$', views.student.resend_consent_form_email, name='resend_consent_form_email'),
    url(r'^signed_consent_form/(?P<profile_id>\d+)/$', views.student.signed_consent_form, name='signed_consent_form'),
    url(r'^unclaimed_progresses/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$', views.mentor.unclaimed_progresses, name='unclaimed_progresses'),
)
