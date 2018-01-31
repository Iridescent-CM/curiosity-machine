from challenges.models import Challenge, Progress
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, TemplateView, UpdateView
from hellosign.models import ConsentTemplate
from profiles.decorators import only_for_role
from profiles.models import UserRole
from profiles.views import EditProfileMixin
from surveys import get_survey
from .aichallenge import Stage
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

class DashboardMixin:
    def get_context_data(self, **kwargs):
        program = self.request.user.membership_set.first() # FIXME?: lazily assume families aren't in multiple
        program_name = program.display_name if program else None
        return super().get_context_data(
            **kwargs,
            program_name=program_name
        )

class HomeView(DashboardMixin, TemplateView):
    template_name = "families/home.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            **kwargs,
            stages=[
                Stage(1, self.request.user),
                Stage(2, self.request.user)
            ],
        )

home = only_for_family(HomeView.as_view())

class StageView(DashboardMixin, TemplateView):
    stagenum = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stage = Stage(self.stagenum)

    def get_context_data(self, **kwargs):
        challenges = self.stage.challenges
        request = self.request

        progresses = Progress.objects.filter(owner=request.user).select_related("challenge")
        completed_progresses = [progress for progress in progresses if progress.completed]
        active_progresses = [progress for progress in progresses if not progress.completed]
        completed_prog_by_challenge_id = {p.challenge_id: p for p in completed_progresses}
        active_prog_by_challenge_id = {p.challenge_id: p for p in active_progresses}

        kwargs["progresses"] = active_prog_by_challenge_id
        kwargs["completed"] = completed_prog_by_challenge_id

        kwargs["challenges"] = self.stage.challenges
        kwargs["units"] = self.stage.units
        return super().get_context_data(**kwargs)

stage_1 = only_for_family(StageView.as_view(template_name="families/stages/stage_1.html", stagenum=1))
stage_2 = only_for_family(StageView.as_view(template_name="families/stages/stage_2.html", stagenum=2))

class PrereqInterruptionView(TemplateView):
    template_name = "families/interruption.html"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        presurvey = get_survey(settings.AICHALLENGE_FAMILY_PRE_SURVEY_ID)
        consent = ConsentTemplate(settings.AICHALLENGE_FAMILY_CONSENT_TEMPLATE_ID)
        return super().get_context_data(
            **kwargs,
            presurvey=presurvey.response(self.request.user),
            consent=consent.signature(self.request.user),
        )

prereq_interruption = only_for_family(PrereqInterruptionView.as_view())

conversion = TemplateView.as_view(template_name="families/conversion.html")
