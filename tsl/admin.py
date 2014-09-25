from django.contrib import admin
from .models import Question, Answer
# Register your models here.

class QuestionAdmin(admin.ModelAdmin):
    model = Question
    list_display = ('id','question_text')

admin.site.register(Question, QuestionAdmin)

class AnswerAdmin(admin.ModelAdmin):
    model = Answer
    list_display = ('id', 'answer_text')

admin.site.register(Answer, AnswerAdmin)
