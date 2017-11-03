from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView
from profiles.models import UserRole
from .models import StudentProfile

class CreateProfileView(CreateView):
    model = StudentProfile
    fields = '__all__'
    success_url = '/home/'

    def form_valid(self, form):
        self.request.user.extra.role = UserRole.student.value
        self.request.user.extra.save()
        return super().form_valid(form)

create = CreateProfileView.as_view()

class EditProfileView(UpdateView):
    model = StudentProfile
    fields = '__all__'

    def get_object(self, queryset=None):
        return self.request.user.studentprofile

edit = EditProfileView.as_view()

def home(request):
    from django.http import HttpResponse
    return HttpResponse('yaaaaay')
