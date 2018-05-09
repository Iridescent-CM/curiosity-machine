from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', make_comment, name='feedback_question')
]
