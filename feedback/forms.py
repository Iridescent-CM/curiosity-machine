from django import forms
from .models import *

class FeedbackForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

        label = self.model.question_text()
        if label:
            answer = forms.CharField(widget=forms.Textarea, required=True)
            self.fields['answer'] = answer

    def get_result(self, user, challenge):
        result = Result(feedback=self.model, user=user)
        setattr(result, 'answer', self.cleaned_data['answer'])
        setattr(result, 'challenge', challenge)
        return result


