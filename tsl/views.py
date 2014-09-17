from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.views.decorators.http import require_http_methods
from django.http import QueryDict, HttpResponse
from .models import Question, Answer
from .forms import AnswerForm
from videos.models import Video 
from images.models import Image

# Create your views here.

@login_required
@require_http_methods(["GET","POST", "DELETE"])
@transaction.atomic
def course_reflection(request):
    questions = Question.objects.order_by('id')
    if request.method == "DELETE":
        form = AnswerForm(data=QueryDict(request.body))
        form.is_valid()
        answer = Answer.objects.get(user_id=request.user.id, question_id=form.cleaned_data['question_id'])
        answer.delete()
        return HttpResponse(status=204)

    if request.method == "POST":
        form = AnswerForm(data=request.POST)

        print(request.POST)
        if form.is_valid():
            video = Video.from_source_with_job(form.cleaned_data['video_filepicker_url']) if form.cleaned_data['video_filepicker_url'] else None
            image = Image.from_source_with_job(form.cleaned_data['picture_filepicker_url']) if form.cleaned_data['picture_filepicker_url'] else None
            try:
                answer = Answer.objects.get(user_id=request.user.id, question_id=form.cleaned_data['question_id'])
            except Answer.DoesNotExist:
                answer = Answer(user=request.user, question_id=form.cleaned_data['question_id'])
            if image: answer.image = image
            if video: answer.video = video
            if form.cleaned_data['answer']: answer.answer_text = form.cleaned_data['answer']
            answer.save()
    answers = [Answer.get_or_build(request.user, q.id) for q in questions]
    forms = [AnswerForm(initial={'question_id': a.question_id, 'answer': a.answer_text}) for a in answers]
    return render(request, 'tsl.html', {'questions': questions, 'forms': forms, 'answers': answers})

