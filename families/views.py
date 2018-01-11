from django.contrib import messages
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from profiles.decorators import only_for_role
from profiles.models import UserRole
from profiles.views import EditProfileMixin
from .forms import *
from .models import *

only_for_family = only_for_role(UserRole.family)

class FamilyMemberMixin():
    def form_valid(self, form):
        formset = self.get_formset()
        if formset.is_valid():
            formset.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please fix the errors below.")
        return super().form_invalid(form)

    def get_formset(self):
        if self.request.method in ('POST', 'PUT'):
            return FamilyMemberFormset(self.request.POST, self.request.FILES, instance=self.request.user)
        else:
            return FamilyMemberFormset(instance=self.request.user)

    def get_context_data(self, **context):
        context['formset'] = self.get_formset()
        return super().get_context_data(**context)

class CreateView(FamilyMemberMixin, EditProfileMixin, CreateView):
    model = FamilyProfile
    form_class = FamilyProfileForm
    success_url = lazy(reverse, str)("families:home")

#create = only_for_role(UserRole.none)(CreateView.as_view())
create = CreateView.as_view()

class EditView(FamilyMemberMixin, EditProfileMixin, UpdateView):
    model = FamilyProfile
    form_class = FamilyProfileForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("families:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.familyprofile

edit = only_for_family(EditView.as_view())

class HomeView(TemplateView):
    template_name = "families/home.html"

home = only_for_family(HomeView.as_view())
