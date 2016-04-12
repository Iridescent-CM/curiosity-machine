from django.conf.urls import patterns, url

urlpatterns = patterns('cmcomments.views',
    url(r'^$', 'comments', name='comments')
)
