# from challenges.models import Challenge, Progress
# from challenges.models import Stage as CommentStage
# from curiositymachine.presenters import LearningSet
# from django.conf import settings
# from lessons.models import Lesson
# from lessons.models import Progress as LessonProgress
# from units.models import Unit

# def get_stages(user=None):
#     return [Stage.from_config(3, user=user)]

# class Stage(LearningSet):
#     @classmethod
#     def from_config(cls, stagenum, user=None, config=None):
#         lessons = Lesson.objects.filter(draft=False)

#         progresses = []
#         if user:
#             progresses = LessonProgress.objects.filter(
#                 owner=user
#             )

#         return cls(stagenum, lessons, [], progresses)
        

#     def __init__(self, number, challenges, units, user_progresses=[]):
#         super().__init__(challenges, user_progresses)
#         self.number = number
#         self.units = units
