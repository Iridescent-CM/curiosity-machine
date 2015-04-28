from django.conf.urls import patterns, url

urlpatterns = patterns('cmcomments.views',
	url(r'^$', 'comments', name='comments'),
    url(r'^(?P<fmt>html|json)$', 'comments', name='comments'),
    url(r'^(?P<comment_id>\d+)/$', 'feature_as_example', name='feature_as_example'),
    url(r'^(?P<comment_id>\d+)/delete_comment$', 'delete_comment', name='delete_comment'),
    url(r'^(?P<comment_id>\d+)/edit_comment/$', 'edit_comment', name='edit_comment'),
    url(r'^(?P<comment_id>\d+)/edit_comment/(?P<fmt>html|json)$', 'edit_comment', name='edit_comment'),
)
