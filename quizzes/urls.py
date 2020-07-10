from django.conf.urls import url
from .views import *

app_name = "quizzes"

urlpatterns = [
    url(r'^$', make_comment, name='quizzes')
]
