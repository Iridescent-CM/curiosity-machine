from challenges.models import Progress, Favorite, Challenge
from django.contrib import messages
from django.shortcuts import Http404
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, FormView, TemplateView, UpdateView
from parents.models import ParentConnection
from profiles.decorators import only_for_role, UserRole
from profiles.views import UserKwargMixin
from .forms import *
from .models import StudentProfile

only_for_student = only_for_role(UserRole.student)

class CreateView(UserKwargMixin, CreateView):
    model = StudentProfile
    form_class = NewStudentProfileForm
    success_url = lazy(reverse, str)("challenges:challenges")

create = only_for_role(UserRole.none)(CreateView.as_view())

class EditView(UserKwargMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileEditForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("students:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.studentprofile

edit = only_for_student(EditView.as_view())

class HomeView(TemplateView):
    template_name = "students/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        context["filter"] = request.GET.get('filter')

        selected_membership = request.GET.get('membership')
        selected_membership_challenges = []
        if selected_membership:
            try:
                selected_membership = int(selected_membership)
            except:
                raise Http404
            selected_membership_challenges = Challenge.objects.filter(
                membership__id=selected_membership, membership__members=request.user
            ).all()
        context["selected_membership"] = selected_membership
        context["selected_membership_challenges"] = selected_membership_challenges


        context["my_challenges_filters"] = [ 'active', 'completed' ]
        context["favorite_challenges"] = Favorite.objects.filter(student=request.user)

        progresses = Progress.objects.filter(student=request.user).select_related("challenge")
        context["completed_progresses"] = [progress for progress in progresses if progress.completed]
        context["active_progresses"] = [progress for progress in progresses if not progress.completed]
        context["progresses"] = progresses

        context["parent_connections"] = ParentConnection.objects.filter(child_profile=request.user.studentprofile, removed=False)
        context["memberships"] = request.user.membership_set.filter(is_active=True)

        return context

home = only_for_student(HomeView.as_view())

underage = TemplateView.as_view(template_name='students/underage.html')
