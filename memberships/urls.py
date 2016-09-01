from django.conf.urls import patterns, url
from memberships import views

urlpatterns = patterns('memberships.views',
    url(r'^(?P<membership_id>\d+)/$', views.MembershipDetailView.as_view(), name='membership'),
    url(r'^(?P<membership_id>\d+)/challenges/$', views.MembershipChallengeListView.as_view(), name='membership_challenges'),
    url(
        r'^(?P<membership_id>\d+)/challenges/(?P<challenge_id>\d+)/$',
        views.MembershipChallengeDetailView.as_view(),
        name='membership_challenge'
    ),
    url(r'^(?P<membership_id>\d+)/students/$', views.MembershipStudentListView.as_view(), name='membership_students'),
    url(
        r'^(?P<membership_id>\d+)/students/(?P<student_id>\d+)/$',
        views.MembershipStudentDetailView.as_view(),
        name='membership_student'
    ),
)
