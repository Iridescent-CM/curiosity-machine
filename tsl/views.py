from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import transaction
from .models import Question, Answer
from .forms import AnswerFormSet

# Create your views here.

@login_required
@transaction.atomic
def course_reflection(request):
    questions = Question.objects.order_by('id')
    if request.POST:
        formset = AnswerFormSet(data=request.POST)
        if formset.is_valid():
            for form in formset:
                video = Video.from_source_with_job(form.cleaned_data['video_filepicker_url']) if form.cleaned_data['video_filepicker_url'] else None
                image = Image.from_source_with_job(form.cleaned_data['picture_filepicker_url']) if form.cleaned_data['picture_filepicker_url'] else None
                try:
                    answer = Answer.objects.get(user_id=request.user.id, question_id=form.cleaned_data['question_id'])
                except Answer.DoesNotExist:
                    answer = Answer(user=request.user, question_id=form.cleaned_data['question_id'])
                if image: answer.image = image
                if video: answer.video = video
                if form.cleaned_data['answer_text']: answer.answer_text = form.cleaned_data['answer_text']
                answer.save()
    else:
        formset = AnswerFormSet(initial=[{'question_id': q.id, 'answer_text': Answer.get_or_build(request.user, q.id).answer_text} for q in questions])
    return render(request, 'tsl.html', {'questions': questions, 'formset': formset})