from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from pages.models import StaticPage
from .views import root_redirect
import profiles.urls

urlpatterns = patterns('',
    url(r'^$', root_redirect, name='root'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/analytics/$', 'curiositymachine.analytics.analytics', name="analytics"),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
    url(r'^training/', include('training.urls', namespace='training', app_name='training')), # training (mentors only)
    url(r'^about/', 'pages.views.static_page', {'page_id': StaticPage.about.value,}, name='about'),
    url(r'^privacy/', 'pages.views.static_page', {'page_id': StaticPage.privacy.value,}, name='privacy'),
    url(r'^educator/', 'pages.views.static_page', {'page_id': StaticPage.educator.value,}, name='educator'),
    url(r'^mentor/', 'pages.views.static_page', {'page_id': StaticPage.mentor.value,}, name='mentor'),
    url(r'^parents/', 'pages.views.static_page', {'page_id': StaticPage.parents.value,}, name='parents'),
    # password reset URLs -- the "recover" one is modified and so resides in the profiles app
    url(r'^password/recover/(?P<signature>.+)/$', 'password_reset.views.recover_done',
        name='password_reset_sent'),
    url(r'^password/recover/$', 'profiles.views.recover', name='password_reset_recover'),
    url(r'^password/reset/done/$', 'password_reset.views.reset_done', name='password_reset_done'),
    url(r'^password/reset/(?P<token>[\w:-]+)/$', 'password_reset.views.reset',
        name='password_reset_reset'),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^tsl/$', include('tsl.urls', namespace='tsl', app_name='tsl'), name='tsl'),
)
