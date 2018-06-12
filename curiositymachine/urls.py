import notifications.urls
import os
import profiles.views

from allauth.account.views import login, logout
from curiositymachine.analytics import analytics
from curiositymachine.decorators import whitelist
from curiositymachine.export_users import export_users
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
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
    url(r'^accounts/signup/(?P<source>[^/]*)/?$', views.signup_with_source, name="account_signup"),
    url(r'^memberships/(?P<slug>[^/]+)/$', views.signup_to_membership, name="membership_signup"),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^login/$', public(login), name='login'),
    url(r'^logout/$', public(logout), name='logout'),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^student/', include('students.urls', namespace='students', app_name='students')),
    url(r'^parent/', include('parents.urls', namespace='parents', app_name='parents')),
    url(r'^mentor/', include('mentors.urls', namespace='mentors', app_name='mentors')),
    url(r'^educator/', include('educators.urls', namespace='educators', app_name='educators')),
    url(r'^family/', include('families.urls', namespace='families', app_name='families')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
    url(r'^lessons/', include('lessons.urls', namespace='lessons', app_name='lessons')),
    url(r'^surveys/', include('surveys.urls', namespace='surveys', app_name='surveys')),
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

    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^units/', include('units.urls', namespace='units', app_name='units'), name='units'),
    url(r'^s3direct/', include('s3direct.urls')),
    url('^notifications/', include(notifications.urls, namespace='notifications')),
    url(r'^health_check/', public(views.health_check)),
    url(r'^log/', public(views.log), name='log'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
