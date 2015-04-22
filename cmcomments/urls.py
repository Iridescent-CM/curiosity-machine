from django.conf.urls import patterns, url

urlpatterns = patterns('cmcomments.views',
    url(r'^(?P<format>html|json)?$', 'comments', name='comments'),
    url(r'^(?P<comment_id>\d+)/$', 'feature_as_example', name='feature_as_example'),
)
