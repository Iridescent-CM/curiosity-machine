from django.conf.urls import patterns, url
from memberships import views

urlpatterns = patterns('memberships.views',
    url(r'^(?P<membership_id>\d+)/$', views.MembershipDetailView.as_view(), name='membership'),
    url(r'^(?P<membership_id>\d+)/design-challenges$', views.MembershipDesignChallengeView.as_view(), name='design-challenges'),

    # this url should have the DC id instead of "individual-dc" in it
    url(r'^(?P<membership_id>\d+)/individual-dc$', views.MembershipStudentProgressView.as_view(), name='individual-dc'),
    url(r'^(?P<membership_id>\d+)/students$', views.MembershipStudentsView.as_view(), name='students'),

    # hub urls
    # url(
    #     r'^(?P<membership_id>\d+)/design-challenges$',
    #     template_name="memberships/educator/design-challenges.html",
    #     {'active_nav': 'design-challenges'},
    #     name='design-challenges'
    # ),
    # url(
    #     r'^(?P<membership_id>\d+)/students$',
    #     template_name="memberships/educator/students.html",
    #     {'active_nav': 'students'},
    #     name='students'
    # ),
)
