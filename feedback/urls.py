from django.conf.urls import url
from .views import *

urlpatterns = [
    url(r'^(?P<feedback_id>\d+)/', make_feedback_result, name='submit'),
]
