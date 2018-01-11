from challenges.models import Challenge
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from profiles.decorators import only_for_role
from profiles.models import UserRole
from profiles.views import EditProfileMixin
from units.models import Unit
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

class StageView(TemplateView):
    stage = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = settings.AICHALLENGE_STAGES[self.stage]

    def get_context_data(self, **kwargs):
        kwargs["challenges"] = Challenge.objects.filter(id__in=self.config['challenges'])
        kwargs["units"] = Unit.objects.filter(id__in=self.config['units'])
        return super().get_context_data(**kwargs) 

stage_1 = only_for_family(StageView.as_view(template_name="families/stages/stage_1.html", stage=1))
stage_2 = only_for_family(StageView.as_view(template_name="families/stages/stage_2.html", stage=2))
