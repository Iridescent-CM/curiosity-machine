from django.conf.urls import patterns, url
from .views import *

urlpatterns = patterns('quizzes.views',
    url(r'^$', make_comment, name='quizzes')
)
