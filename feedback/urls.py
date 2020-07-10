from django.conf.urls import url
from .views import *

app_name = "feedback"

urlpatterns = [
    url(r'^(?P<feedback_id>\d+)/', make_feedback_result, name='submit'),
]
