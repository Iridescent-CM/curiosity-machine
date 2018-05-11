from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^$', make_feedback_result, name='feedback_question')
]
