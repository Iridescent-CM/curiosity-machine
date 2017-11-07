import notifications.urls
import os
import password_reset.views
import profiles.views

from allauth.account.views import login, logout
from curiositymachine.analytics import analytics
from curiositymachine.decorators import whitelist
from curiositymachine.export_users import export_users
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import password_change
from django.core.urlresolvers import reverse
from django.utils.functional import lazy
from django.views.generic.base import RedirectView, TemplateView
from . import views

public = whitelist('public')

PAGES_DIR = os.path.join(settings.BASE_DIR, 'curiositymachine/templates/curiositymachine/pages')

def pages_urls():
    templates = [f for f in os.listdir(PAGES_DIR) if os.path.isfile(os.path.join(PAGES_DIR, f))]
    urls = []
    for template in templates:
        name = os.path.splitext(template)[0]
        path_re = "^%s/$" % name
        urls.append(url(
            path_re,
            public(TemplateView.as_view(template_name="curiositymachine/pages/%s" % template)),
            name=name
        ))
    return urls

urlpatterns = [
    url(r'^$', public(views.root), name='root'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/analytics/$', analytics, name="analytics"),
    url(r'^admin/export_users/$', export_users, name="export_users"),
    url(r'^accounts/signup/(?P<source>[^/]*)/?$', views.signup_with_source, name="source_account_signup"),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^login/$', public(login), name='login'),
    url(r'^logout/$', public(logout), name='logout'),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^student/', include('students.urls', namespace='students', app_name='students')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
]

# about pages, static pages
urlpatterns += pages_urls()

urlpatterns += [
    # redirects
    url(
        r'^terms-of-use/',
        public(RedirectView.as_view(url='http://iridescentlearning.org/terms-of-use/', permanent=True)),
        name='terms-of-use'
    ),
    url(
        r'^privacy/',
        public(RedirectView.as_view(url='http://iridescentlearning.org/privacy-policy/', permanent=True)),
        name='privacy'
    ),
    url(
        r'^faq/',
        public(RedirectView.as_view(url='https://iridescentsupport.zendesk.com/hc/en-us/categories/115000091368-Curiosity-Machine', permanent=True)),
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
            "post_change_redirect": lazy(reverse, str)('profiles:edit_profile')
        },
        name='password_change'
    ),

    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^units/', include('units.urls', namespace='units', app_name='units'), name='units'),
    url(r'^s3direct/', include('s3direct.urls')),
    url('^notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^health_check/', public(views.health_check)),
    url(r'^log/', public(views.log), name='log'),
]
