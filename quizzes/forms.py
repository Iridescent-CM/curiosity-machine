from django import forms
from .models import Result

class QuizForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)
        for i in range(1, 5):
            choices = ()
            for j in range(1, 5):
                name = self.model.answer_text(i, j)
                choices = choices + ((j, name),)
            self.fields['question_%d' % i] = forms.TypedChoiceField(
                coerce=int,
                widget=forms.RadioSelect,
                label=self.model.question_text(i),
                choices=choices
            )

    def get_result(self, user):
        result = Result(quiz=self.model, user=user)
        for i in range(1, 5):
            setattr(result, 'answer_%d' % i, self.cleaned_data['question_%d' % i])
        return result
        

