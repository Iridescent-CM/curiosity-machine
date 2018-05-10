from django import forms
from .models import *

class FeedbackQuestionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

        answer = forms.CharField(widget=forms.Textarea, required=True)
        self.fields['answer'] = answer

    def get_feedback_result(self, user, challenge):
        feedback_result = FeedbackResult(feedback_question=self.model, user=user)
        setattr(feedback_result, 'answer', self.cleaned_data['answer'])
        setattr(feedback_result, 'challenge', challenge)
        return feedback_result


