from challenges.models import Challenge, Progress
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

class StageView(TemplateView):
    stage = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = settings.AICHALLENGE_STAGES[self.stage]

    def get_context_data(self, **kwargs):
        challenges = sorted(
            Challenge.objects.filter(id__in=self.config['challenges']),
            key=lambda c: self.config['challenges'].index(c.id)
        )

        progresses = Progress.objects.filter(owner=self.request.user, challenge_id__in=self.config['challenges'])
        prog_by_challenge_id = {p.challenge_id: p for p in progresses}
        for challenge in challenges:
            if challenge.id in prog_by_challenge_id:
                # decorate here with level of progress for visual representation
                pass

        kwargs["challenges"] = challenges
        kwargs["units"] = sorted(
            Unit.objects.filter(id__in=self.config['units']),
            key=lambda u: self.config['units'].index(u.id)
        )
        return super().get_context_data(**kwargs)

stage_1 = only_for_family(StageView.as_view(template_name="families/stages/stage_1.html", stage=1))
stage_2 = only_for_family(StageView.as_view(template_name="families/stages/stage_2.html", stage=2))
