from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^(?P<challenge_id>\d+)/(?P<username>[\w.@+-]+)/feedback/(?P<feedback_id>\d+)/', make_feedback_result, name='feedback_question'),
]
