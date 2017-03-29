from django import forms
from .models import *

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)
        for i in range(1, QUESTION_COUNT+1):
            choices = ()
            label = self.model.question_text(i)
            if label:
                for j in range(1, MAX_ANSWERS+1):
                    name = self.model.answer_text(i, j)
                    if name:
                        choices = choices + ((j, name),)
                self.fields['question_%d' % i] = forms.TypedChoiceField(
                    coerce=int,
                    widget=forms.RadioSelect,
                    label=self.model.question_text(i),
                    choices=choices
                )

    def get_result(self, user):
        result = Result(quiz=self.model, user=user)
        for i in range(1, QUESTION_COUNT+1):
            k = 'question_%d' % i
            if k in self.cleaned_data:
                setattr(result, 'answer_%d' % i, self.cleaned_data[k])
        return result
        

