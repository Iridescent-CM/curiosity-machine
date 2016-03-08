from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout, password_change
from django.views.generic.base import RedirectView, TemplateView
from django.utils.functional import lazy
from django.core.urlresolvers import reverse
from curiositymachine.decorators import whitelist
from . import views
import password_reset.views
import profiles.urls
import profiles.views

public = whitelist('public')

urlpatterns = patterns('',
    url(r'^$', public(views.root), name='root'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/analytics/$', 'curiositymachine.analytics.analytics', name="analytics"),
    url(r'^admin/export_users/$', 'curiositymachine.export_users.export_users', name="export_users"),
    url(r'^login/$', public(login), name='login'),
    url(r'^logout/$', public(logout), name="logout"),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
    url(r'^training/', include('training.urls', namespace='training', app_name='training')), # training (mentors only)

    # about pages
    url(
        r'^about/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/about.html")),
        {'active_nav': 'about'},
        name='about'
    ),
    url(
        r'^educator/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/educator.html")),
        {'active_nav': 'educator'},
        name='educator'
    ),
    url(
        r'^mentor/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/mentor.html")),
        {'active_nav': 'mentor'},
        name='mentor'
    ),
    url(
        r'^parents/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/parents.html")),
        {'active_nav': 'parents'},
        name='parents'
    ),
    url(
        r'^about-membership/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/about-membership.html")),
        {'active_nav': 'membership'},
        name='about-membership'
    ),
    url(
        r'^about-partnership/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/about-partnership.html")),
        {'active_nav': 'partnership'},
        name='about-partnership'
    ),
    url(
        r'^about-technical-communication/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/about-technical-communication.html")),
        # {'active_nav': 'partnership'},
        name='about-technical-communication'
    ),
    url(
        r'^faq/',
        public(TemplateView.as_view(template_name="curiositymachine/pages/faq.html")),
        {'active_nav': 'faq'},
        name='faq'
    ),

    # password reset URLs -- the "recover" one is modified and so resides in the profiles app
    url(r'^password/recover/(?P<signature>.+)/$', public(password_reset.views.recover_done),
        name='password_reset_sent'),
    url(r'^password/recover/$', public(profiles.views.recover), name='password_reset_recover'),
    url(r'^password/reset/done/$', public(password_reset.views.reset_done), name='password_reset_done'),
    url(r'^password/reset/(?P<token>[\w:-]+)/$', public(password_reset.views.reset),
        name='password_reset_reset'),

    url(r'^password/change$',
        public(password_change),
        {
            "post_change_redirect": lazy(reverse, str)('profiles:profile_edit')
        },
        name='password_change'
    ),

    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^tsl/$', include('tsl.urls', namespace='tsl', app_name='tsl'), name='tsl'),
    url(r'^units/', include('units.urls', namespace='units', app_name='units'), name='units'),
    url(r'^s3direct/', include('s3direct.urls')),
    url(r'^groups/', include('groups.urls', namespace='groups', app_name='groups'), name='groups'),
    url(r'^health_check/', public(views.health_check)),
)
