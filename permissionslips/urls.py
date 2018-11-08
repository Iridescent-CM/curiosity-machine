from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^new/$', SignSlipView.as_view(), name="create_permissionslip"),
]