from challenges.models import Challenge, Progress
from curiositymachine.decorators import whitelist
from curiositymachine.presenters import LearningSet, get_stages
from django.conf import settings
from django.contrib import messages
from django.http import *
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import *
from hellosign import jobs
from lessons.models import Lesson
from lessons.models import Progress as LessonProgress
from profiles.decorators import not_for_role, only_for_role
from profiles.models import UserRole
from profiles.views import EditProfileMixin
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from surveys import get_survey
# from .aichallenge import get_stages, Stage
from .awardforce import *
from .forms import *
from .models import *
from .serializers import *
from django.conf import settings

only_for_family = only_for_role(UserRole.family)
unapproved_ok = whitelist('unapproved_family')

class FamilyMemberMixin():
    def form_valid(self, form):
        profile = getattr(self.request.user, 'familyprofile', None)
        if profile and profile.members_confirmed:
            return super().form_valid(form)
        else:
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

class CreateProfileView(FamilyMemberMixin, EditProfileMixin, CreateView):
    model = FamilyProfile
    form_class = FamilyProfileForm
    success_url = lazy(reverse, str)("families:home")

create = not_for_role(UserRole.family, redirect="families:edit_profile")(CreateProfileView.as_view())

class EditView(FamilyMemberMixin, EditProfileMixin, UpdateView):
    model = FamilyProfile
    form_class = FamilyProfileForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("families:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.familyprofile

edit = unapproved_ok(only_for_family(EditView.as_view()))

class DashboardMixin:
    def get_context_data(self, **kwargs):
        program = self.request.user.membership_set.first() # FIXME?: lazily assume families aren't in multiple
        program_name = program.display_name if program else None
        return super().get_context_data(
            **kwargs,
            program_name=program_name
        )

class HomeView(DashboardMixin, ListView):
    template_name = "families/home.html"
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = 'activity'

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs, lesson_set=LearningSet.from_config(user=self.request.user),)

        by_day = {}
        for notification in context['activity']:
            day = notification.timestamp.date()
            by_day[day] = by_day.get(day, [])
            by_day[day].append(notification)

        context.update({
            "activity_by_day": by_day,
        })

        return context

home = only_for_family(HomeView.as_view())

class StageView(DashboardMixin, TemplateView):
    stagenum = None

    def get_context_data(self, **kwargs):
        stage = LearningSet.from_config(self.stagenum, user=self.request.user)
        kwargs["challenges"] = stage.objects
        kwargs["units"] = stage.units
        return super().get_context_data(**kwargs)

stage_1 = only_for_family(StageView.as_view(template_name="families/stages/stage_1.html", stagenum=1))
stage_2 = only_for_family(StageView.as_view(template_name="families/stages/stage_2.html", stagenum=2))

class LessonsView(DashboardMixin, TemplateView):
    template_name = "families/stages/stage_3.html"

    def get_context_data(self, **kwargs):
        stage = LearningSet.from_config(user=self.request.user)
        kwargs["lessons"] = stage.lessons
        return super().get_context_data(**kwargs)

stage_3 = only_for_family(LessonsView.as_view())

class PrereqInterruptionView(TemplateView):
    template_name = "families/interruption.html"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        presurvey = get_survey(settings.AICHALLENGE_FAMILY_PRE_SURVEY_ID)
        return super().get_context_data(
            **kwargs,
            presurvey=presurvey.response(self.request.user),
            email_form=FamilyEmailForm(request=self.request, user=self.request.user),
        )

prereq_interruption = only_for_family(PrereqInterruptionView.as_view())

class PostSurveyInterruptionView(TemplateView):
    template_name = "families/post_survey.html"

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        postsurvey = get_survey(settings.AICHALLENGE_FAMILY_POST_SURVEY_ID)
        return super().get_context_data(
            **kwargs,
            postsurvey=postsurvey.response(self.request.user),
        )

postsurvey_interruption = only_for_family(PostSurveyInterruptionView.as_view())

conversion = TemplateView.as_view(template_name="families/conversion.html")

class SubmissionView(DashboardMixin, TemplateView):
    def get_template_names(self):
        if settings.AICHALLENGE_SEASON_OPEN:
            template = "families/submission.html"
        else:
            template = "families/submission_closed.html"
        return template

submission = only_for_family(SubmissionView.as_view())

class AwardForceRedirectView(View):

    def get(self, request, *args, **kwargs):
        return Integrating(request.user).run()

awardforce = only_for_family(AwardForceRedirectView.as_view())

class SubmissionChecklistViewSet(viewsets.ViewSet):

    def list(self, request):
        return Response(ChecklistSerializer(AwardForceChecklist(request.user)).data)

    @action(methods=['post'], detail=False)
    def confirm_family(self, request):
        AwardForceChecklist(request.user).confirm_family_members()
        return Response({'status': 'family members confirmed'})

    @action(methods=['post'], detail=False)
    def resend_verification(self, request):
        AwardForceChecklist(request.user).resend_verification_email(self.request)
        return Response({'status': 'ok'})

    @action(methods=['post'], detail=False)
    def change_email(self, request):
        form = UnusedEmailForm(data=request.data)
        if form.is_valid():
            obj = EmailAddress.objects.add_email(
                self.request,
                self.request.user,
                form.cleaned_data["email"],
                confirm=True
            )
            obj.set_as_primary()
            return Response({'status': 'changed'})
        else:
            return Response({
                'status': 'error',
                'errors': form.errors.as_data()
            })

class SignPermissionSlipView(CreateView):
    model = PermissionSlip
    fields = ('signature',)
    success_url = lazy(reverse, str)("families:home")

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.account = self.request.user
        obj.save()
        self.object = obj
        return HttpResponseRedirect(self.get_success_url())

sign_slip = only_for_family(SignPermissionSlipView.as_view())
