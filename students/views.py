from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView
from .models import StudentProfile

class CreateProfileView(CreateView):
    model = StudentProfile
    fields = '__all__'
    success_url = 'student/profile/%(id)d/edit'

create = CreateProfileView.as_view()

class EditProfileView(UpdateView):
    model = StudentProfile
    fields = '__all__'

edit = EditProfileView.as_view()
