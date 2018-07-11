from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from .views import *

router = SimpleRouter()
router.register(r'lesson', LessonViewSet, base_name="lesson")
router.register(r'lesson_progress', LessonProgressViewSet, base_name="lesson-progress")
router.register(r'comment', CommentViewSet, base_name="comment")
router.register(r'quiz', QuizViewSet, base_name="quiz")
router.register(r'quiz_result', QuizResultViewSet, base_name="quiz-result")
urlpatterns = router.urls