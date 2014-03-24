from django.conf.urls import patterns, include, url
from django.contrib import admin
import profiles.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'curiositymachine.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^login/$', 'django.contrib.auth.views.login', name='login'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', name="logout"),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
)
