from django.conf.urls import patterns, include, url
from django.contrib import admin
import profiles.urls

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'curiositymachine.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('cmauth.urls', namespace='cmauth', app_name='cmauth')),
    url(r'^', include('profiles.urls', namespace='profiles', app_name='profiles')),
    url(r'^challenges/', include('challenges.urls', namespace='challenges', app_name='challenges')),
)
