from django import forms
from .models import MentorProfile

class EditStudentProfileForm(forms.ModelForm):
    class Meta:
        model = MentorProfile
        fields = '__all__'
