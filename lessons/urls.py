from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from curiositymachine.decorators import whitelist
from .views import *

public = whitelist('public')

router = SimpleRouter()
router.register(r'lesson', LessonViewSet, base_name="lesson")
router.register(r'lesson_progress', LessonProgressViewSet, base_name="lesson-progress")
router.register(r'comment', CommentViewSet, base_name="comment")
router.register(r'quiz', QuizViewSet, base_name="quiz")
router.register(r'quiz_result', QuizResultViewSet, base_name="quiz-result")
urlpatterns = router.urls

# rest_framework doesn't have a good affordance for decorators, so
# for now we're replacing the LessonViewSet list route with a whitelisted version
# this way (FIXME)
urlpatterns += [
    url(r'^lesson/$', public(LessonViewSet.as_view({'get':'list'})), name='lesson-list')
]