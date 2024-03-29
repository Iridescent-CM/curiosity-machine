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
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic.base import RedirectView, TemplateView
from . import views

public = whitelist('public')

PAGES_DIR = os.path.join(settings.BASE_DIR, 'curiositymachine/templates/curiositymachine/pages')

def pages_urls():
    """
    Routes some/path/to/file.html as /some/path/to/file/ on the site.
    """

    templates = []
    for dirpath, names, files in os.walk(PAGES_DIR):
        dirpath = os.path.relpath(dirpath, PAGES_DIR)
        dirpath = '' if dirpath == '.' else dirpath
        templates.extend([os.path.join(dirpath, f) for f in files])
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
    url(r'^admin/', admin.site.urls),
    url(r'^admin/analytics/$', analytics, name="analytics"),
    url(r'^admin/export_users/$', export_users, name="export_users"),
    url(r'^accounts/signup/(?P<source>[^/]*)/?$', views.signup_with_source, name="account_signup"),
    url(r'^memberships/(?P<slug>[^/]+)/$', views.signup_to_membership, name="membership_signup"),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^login/$', public(login), name='login'),
    url(r'^logout/$', public(logout), name='logout'),
    url(r'^', include('profiles.urls')),
    url(r'^student/', include('students.urls')),
    url(r'^educator/', include('educators.urls')),
    url(r'^family/', include('families.urls')),
    url(r'^challenges/', include('challenges.urls')),
    url(r'^lessons/', include('lessons.urls')),
    url(r'^surveys/', include('surveys.urls')),
    url(r'^django-rq/', include('django_rq.urls')), # task queue manager (staff users only)
]

urlpatterns += [
    # redirect url that used to be a static page
    url(
        r'^aichallenge/worldchampionship/',
        public(
            RedirectView.as_view(
                url='https://www.technovation.org/blogs/technovation-families-finalists-regional-winners/',
                permanent=False
            )
        ),
        name='aichallenge-worldchampionship-redirect'
    ),
]

# about pages, static pages
urlpatterns += pages_urls()

urlpatterns += [
    # redirects
    url(
        r'^terms-of-use/',
        public(RedirectView.as_view(url='https://www.technovation.org/terms-of-use/', permanent=True)),
        name='terms-of-use'
    ),
    url(
        r'^privacy/',
        public(RedirectView.as_view(url='https://www.technovation.org/privacy-policy/', permanent=True)),
        name='privacy'
    ),
    url(
        r'^faq/',
        public(RedirectView.as_view(url='https://iridescentsupport.zendesk.com/hc/en-us/categories/115000091368-Technovation-Families', permanent=True)),
        name='faq'
    ),
    url(
        r'^aichallenge/coaches/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='coaches'
    ),
    url(
        r'^aichallenge/families/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='families'
    ),
        url(
        r'^aichallenge/timeline/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='timeline'
    ),
        url(
        r'^educator/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='educator'
    ),
    url(
        r'^parents/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='parents'
    ),
    url(
        r'^families/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='families'
    ),
    url(
        r'^about-partnership/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='about-partnership'
    ),
    url(
        r'^program-leaders/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='program leaders'
    ),
    url(
        r'^aichallenge/$',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='aichallenge'
    ),

    url(
        r'^about/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='about'
    ),

    url(
        r'^community-guidelines/',
        public(RedirectView.as_view(url="/get-started", permanent=True)),
        name='community-guidelines'
    ),

    url(r'^summernote/', include('django_summernote.urls')),
    url(r'^units/', include('units.urls'), name='units'),
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
