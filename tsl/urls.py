from django.conf.urls import patterns, url

urlpatterns = patterns('tsl.views',
    url(r'^$', 'course_reflection', name='course_reflection'),
)
