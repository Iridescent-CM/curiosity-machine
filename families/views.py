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

class CreateView(EditProfileMixin, CreateView):
    model = FamilyProfile
    form_class = FamilyProfileForm
    success_url = lazy(reverse, str)("families:home")

#create = only_for_role(UserRole.none)(CreateView.as_view())
create = CreateView.as_view()

class EditView(EditProfileMixin, UpdateView):
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
