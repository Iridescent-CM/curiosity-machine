from django.conf.urls import url
from . import views

app_name = "comments"

urlpatterns = [
    url(r'^$', views.comments, name='comments')
]
