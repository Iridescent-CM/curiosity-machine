from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic.base import RedirectView
from curiositymachine.decorators import whitelist
from pages.models import StaticPage
from .views import root, health_check
import password_reset.views
import profiles.urls
import profiles.views
import pages.views

public = whitelist('public')

urlpatterns = patterns('',
    url(r'^$', public(root), name='root'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/analytics/$', 'curiositymachine.analytics.analytics', name="analytics"),
    url(r'^admin/export_users/$', 'curiositymachine.export_users.export_users', name="export_users"),
    url(r'^login/$', public(login), name='login'),
    url(r'^logout/$', public(logout), name="logout"),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
    url(r'^training/', include('training.urls', namespace='training', app_name='training')), # training (mentors only)
    url(r'^about/', public(pages.views.static_page), {'page_id': StaticPage.about.value,}, name='about'),
    url(r'^privacy/', public(pages.views.static_page), {'page_id': StaticPage.privacy.value,}, name='privacy'),
    url(r'^educator/', public(pages.views.static_page), {'page_id': StaticPage.educator.value,}, name='educator'),
    url(r'^mentor/', public(pages.views.static_page), {'page_id': StaticPage.mentor.value,}, name='mentor'),
    url(r'^parents/', public(pages.views.static_page), {'page_id': StaticPage.parents.value,}, name='parents'),
    url(r'^faq/', public(pages.views.static_page), {'page_id': StaticPage.faq.value,}, name='faq'),
    # password reset URLs -- the "recover" one is modified and so resides in the profiles app
    url(r'^password/recover/(?P<signature>.+)/$', public(password_reset.views.recover_done),
        name='password_reset_sent'),
    url(r'^password/recover/$', public(profiles.views.recover), name='password_reset_recover'),
    url(r'^password/reset/done/$', public(password_reset.views.reset_done), name='password_reset_done'),
    url(r'^password/reset/(?P<token>[\w:-]+)/$', public(password_reset.views.reset),
        name='password_reset_reset'),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^tsl/$', include('tsl.urls', namespace='tsl', app_name='tsl'), name='tsl'),
    url(r'^units/', include('units.urls', namespace='units', app_name='units'), name='units'),
    url(r'^s3direct/', include('s3direct.urls')),
    url(r'^groups/', include('groups.urls', namespace='groups', app_name='groups'), name='groups'),
    url(r'^health_check/', public(health_check)),
)
