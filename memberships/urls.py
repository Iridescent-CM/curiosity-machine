from django.conf.urls import patterns, url
from memberships import views

urlpatterns = patterns('memberships.views',
    url(r'^(?P<membership_id>\d+)/$', views.MembershipDetailView.as_view(), name='membership'),
)
