from django.conf.urls import url, include
from rest_framework import routers
from .views import *

#router = routers.SimpleRouter()
#router.register(r'(?P<lesson_pk>\d+)/uploads', UploadViewSet, base_name='upload')

#urlpatterns = router.urls + [
urlpatterns = [
    url(r'^(?P<pk>\d+)/pages/(?P<page>[^/]+)/$', show_page, name='page'),
]

from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r'lesson', LessonViewSet, base_name="lesson")
router.register(r'lesson_progress', LessonProgressViewSet, base_name="lesson-progress")
urlpatterns += router.urls