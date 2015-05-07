from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic.base import RedirectView
from pages.models import StaticPage
from .views import root_redirect
import profiles.urls
from django.views.generic.base import TemplateView

urlpatterns = patterns('',
    url(r'^$', root_redirect, name='root'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/analytics/$', 'curiositymachine.analytics.analytics', name="analytics"),
    url(r'^admin/export_users/$', 'curiositymachine.export_users.export_users', name="export_users"),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
    url(r'^training/', include('training.urls', namespace='training', app_name='training')), # training (mentors only)
    url(r'^about/', TemplateView.as_view(template_name="static/about.html"), name='about'),
    url(r'^privacy/', TemplateView.as_view(template_name="static/privacy.html"), name='privacy'),
    url(r'^educator/', 'pages.views.static_page', {'page_id': StaticPage.educator.value,}, name='educator'),
    url(r'^mentor/', TemplateView.as_view(template_name="static/mentor.html"), name='mentor'),
    url(r'^parents/', TemplateView.as_view(template_name="static/parent.html"), name='parents'),
    url(r'^faq/', TemplateView.as_view(template_name="static/faq.html"), name='faq'),
    # password reset URLs -- the "recover" one is modified and so resides in the profiles app
    url(r'^password/recover/(?P<signature>.+)/$', 'password_reset.views.recover_done',
        name='password_reset_sent'),
    url(r'^password/recover/$', 'profiles.views.recover', name='password_reset_recover'),
    url(r'^password/reset/done/$', 'password_reset.views.reset_done', name='password_reset_done'),
    url(r'^password/reset/(?P<token>[\w:-]+)/$', 'password_reset.views.reset',
        name='password_reset_reset'),
    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^tsl/$', include('tsl.urls', namespace='tsl', app_name='tsl'), name='tsl'),
    url(r'^units/', include('units.urls', namespace='units', app_name='units'), name='units'),
    url(r'^s3direct/', include('s3direct.urls')),
    url(r'^groups/', include('groups.urls', namespace='groups', app_name='groups'), name='groups'),
)
