from allauth.account.forms import SetPasswordForm
from challenges.models import Challenge, Example
from cmcomments.forms import CommentForm
from cmcomments.models import Comment
from curiositymachine import signals
from curiositymachine.decorators import whitelist
from django.conf import settings
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import PermissionDenied
from django.db.models import Prefetch, Q
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, FormView, ListView, RedirectView, TemplateView, UpdateView, View
from memberships.helpers.selectors import GroupSelector
from memberships.models import Member, Membership
from profiles.decorators import only_for_role, UserRole
from profiles.views import EditProfileMixin
from rest_framework import generics, permissions
from rest_framework.renderers import JSONRenderer
from rest_framework.permissions import IsAuthenticated
from units.models import Unit
from .annotators import *
from .decorators import *
from .forms import *
from .models import *
from .serializers import *
from .sorting import *
from django.conf import settings
from surveys import get_survey
from surveys.models import SurveyResponse


only_for_educator = only_for_role(UserRole.educator)

class CreateView(EditProfileMixin, CreateView):
    model = EducatorProfile
    form_class = EducatorProfileForm
    success_url = lazy(reverse, str)("educators:home")

create = only_for_role(UserRole.none)(CreateView.as_view())

class EditView(EditProfileMixin, UpdateView):
    model = EducatorProfile
    form_class = EducatorProfileForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("educators:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.educatorprofile

edit = only_for_educator(EditView.as_view())

class ChallengesView(TemplateView):
    template_name = "educators/dashboard/challenges.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        core_challenges = Challenge.objects.filter(draft=False, core=True).select_related('image').prefetch_related('resource_set')

        membership_challenges = []
        membership = None
        gs = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            gs = GroupSelector(membership)
            membership_challenges = membership.challenges.select_related('image').prefetch_related('resource_set')
            core_challenges = core_challenges.exclude(id__in=membership_challenges.values('id'))

        context.update({
            "membership": membership,
            "membership_challenges": membership_challenges,
            "core_challenges": core_challenges,
            "membership_selection": membership_selection,
            "group_selector": gs,
        })

        return context

challenges = only_for_educator(ChallengesView.as_view())

class ChallengeView(TemplateView):
    template_name = "educators/dashboard/challenge.html"

    def get_context_data(self, **kwargs):
        membership_selection = MembershipSelection(self.request)
        if not membership_selection.selected:
            raise PermissionDenied

        membership = membership_selection.selected
        challenge = get_object_or_404(membership.challenges, pk=self.kwargs.get('challenge_id'))

        sorter = StudentSorter(query=self.request.GET)
        gs = GroupSelector(membership, query=self.request.GET)
        students = gs.selected.queryset
        students = sorter.sort(students)
        students = students.all()

        comments = (Comment.objects
            .filter(
                user__in=students,
                challenge_progress__challenge_id=challenge.id)
            .select_related('user'))
        student_ids_with_examples = (Example.objects
            .filter(
                approved=True,
                progress__challenge_id=challenge.id,
                progress__owner__in=students)
            .values_list('progress__owner__id', flat=True))

        for student in students:
            UserCommentSummary(comments, student.id).annotate(student)

        kwargs.update({
            "challenge": challenge,
            "challenge_links": membership.challenges.order_by('name').all(),
            "students": students,
            "student_ids_with_examples": student_ids_with_examples,
            "membership_selection": membership_selection,
            "sorter": sorter,
            "group_selector": gs,
        })
        return super().get_context_data(**kwargs)

challenge = only_for_educator(ChallengeView.as_view())

class StudentsView(TemplateView):
    template_name = "educators/dashboard/students.html"

    def get_context_data(self, **kwargs):
        request = self.request
        membership = None
        students = []
        sorter = None
        gs = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            sorter = StudentSorter(query=request.GET)
            gs = GroupSelector(membership, query=request.GET)
            students = gs.selected.queryset
            students = sorter.sort(students)

        kwargs.update({
            "membership": membership,
            "students": students,
            "group_selector": gs,
            "membership_selection": membership_selection,
            "sorter": sorter,
        })
        return super().get_context_data(**kwargs)

students = only_for_educator(StudentsView.as_view())

class StudentView(TemplateView):
    template_name = "educators/dashboard/student.html"

    def get_context_data(self, **kwargs):
        membership_selection = MembershipSelection(self.request)
        if not membership_selection.selected:
            raise PermissionDenied

        membership = membership_selection.selected
        listed_members = membership.listed_members
        member = get_object_or_404(listed_members, pk=self.kwargs.get('student_id'))
        progresses = (member.progresses
            .filter(comments__isnull=False, challenge__in=membership.challenges.all())
            .select_related('challenge', 'mentor')
            .prefetch_related(
                'comments',
                Prefetch('example_set', queryset=Example.objects.status(approved=True), to_attr='approved_examples')
            )
            .distinct()
            .all())

        for progress in progresses:
            UserCommentSummary(progress.comments.all(), member.id).annotate(progress)
        sorter = ProgressSorter(query=self.request.GET)
        progresses = sorter.sort(progresses)

        graph_data_url = "%s?%s" % (reverse('educators:progress_graph_data'), "&".join(["id=%d" % p.id for p in progresses]))

        kwargs.update({
            "student": member,
            "progresses": progresses,
            "completed_count": len([p for p in progresses if p.complete]),
            "membership_selection": membership_selection,
            "sorter": sorter,
            "graph_data_url": graph_data_url,
        })
        return super().get_context_data(**kwargs)

student = only_for_educator(StudentView.as_view())

class StudentPasswordResetView(FormView):
    template_name = "educators/dashboard/password_reset.html"
    form_class = SetPasswordForm
    success_url = lazy(reverse, str)("educators:students")

    def dispatch(self, request, *args, **kwargs):
        self.membership_selection = MembershipSelection(request)
        membership = self.membership_selection.selected
        listed_members = membership.listed_members
        self.member = get_object_or_404(listed_members, pk=self.kwargs.get('student_id'))
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({
            "user": self.member
        })
        return kwargs

    def get_context_data(self, **kwargs):
        kwargs.update({
            "student": self.member,
            "membership_selection": self.membership_selection
        })
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        form.save()
        signals.member_password_changed.send(
            sender=self.member,
            member=self.member,
            resetter=self.request.user
        )
        messages.success(self.request, "%s's password successfully changed." % self.member.username)
        return super().form_valid(form)

student_password_reset = only_for_educator(StudentPasswordResetView.as_view())

class GuidesView(TemplateView):
    template_name = "educators/dashboard/guides.html"

    def get_context_data(self, **kwargs):
        units = Unit.objects.filter(listed=True).order_by('id').select_related('image')

        extra_units = []
        membership = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            extra_units = membership.extra_units.order_by('id').select_related('image')
            units = units.exclude(id__in=extra_units.values('id'))

        kwargs.update({
            "units": units,
            "membership": membership,
            "extra_units": extra_units,
            "membership_selection": membership_selection,
        })

        return super().get_context_data(**kwargs)

guides = only_for_educator(GuidesView.as_view())

class ImpactSurveySubmitView(View):
    http_method_names=['post']

    def post(self, request, *args, **kwargs):
        survey = ImpactSurvey.objects.create(user=request.user)
        form = ImpactSurveyForm(data=request.POST, instance=survey)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({
                "status": "invalid",
                "errors": form.errors
            }, status=400)

impact_data = whitelist('public')(
    only_for_educator(
        ImpactSurveySubmitView.as_view()))

class IsEducator(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.extra.is_educator

class CommentList(generics.ListAPIView):
    renderer_classes = (JSONRenderer,)
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticated, IsEducator)

    def get_queryset(self):
        queryset = Comment.objects.none()
        ids = self.request.query_params.getlist('id', None)
        if ids is not None:
            queryset = (Comment.objects
                .filter(challenge_progress__owner__membership__members=self.request.user)
                .filter(challenge_progress_id__in=ids)
                .select_related('challenge_progress')
                .all()
            )
        return queryset

comments = whitelist('public')(CommentList.as_view())

class CoachView(RedirectView):
    pattern_name = "educators:create_profile"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.membership_id = settings.AICHALLENGE_COACH_MEMBERSHIP_ID

    def get(self, request, *args, **kwargs):
        member, created = Member.objects.get_or_create(user=request.user, membership_id=self.membership_id)
        return super().get(request, *args, **kwargs)

coach = CoachView.as_view()

class CoachConversionView(View):
    http_method_names = ['post', 'get']

    def get(self, request, *args, **kwargs):
        if request.user.educatorprofile.is_coach:
          messages.success(self.request, "You are already in the AI family coach membership!")
          return HttpResponseRedirect(reverse("educators:home"))
        else:
          return render(request, 'educators/coach_conversion.html')

    def post(self, request, *args, **kwargs):
        membership = Membership.objects.get(pk=settings.AICHALLENGE_COACH_MEMBERSHIP_ID)
        member = Member(user=self.request.user, membership=membership)
        member.save()

        messages.success(self.request, "You are now in the AI Family Challenge Coach membership! Enjoy the resources under Units & Guides.")
        return HttpResponseRedirect(reverse("educators:home"))

coach_conversion = only_for_educator(CoachConversionView.as_view())

class ConversationView(TemplateView):
    template_name = "educators/dashboard/conversation.html"

    def get_context_data(self, **kwargs):
        membership_selection = MembershipSelection(self.request)
        if not membership_selection.selected:
            raise PermissionDenied

        membership = membership_selection.selected
        student = get_object_or_404(membership.members, pk=kwargs.pop("student_id"))
        progress = get_object_or_404(student.progresses, challenge_id=kwargs.pop("challenge_id"))

        progress_type = ContentType.objects.get_for_model(progress)
        self.request.user.notifications.all().filter(
            Q(
                verb="completed",
                action_object_content_type=progress_type,
                action_object_object_id=progress.id
            ) | Q(
                verb="posted",
                target_content_type=progress_type,
                target_object_id=progress.id
            )
        ).mark_all_as_read()

        return super().get_context_data(
            membership_selection=membership_selection,
            student=student,
            progress=progress,
            comments=progress.comments.order_by("-created").all(),
            comment_form=CommentForm(),
            **kwargs
        )

conversation = only_for_educator(ConversationView.as_view())

class ActivityView(ListView):
    template_name = "educators/dashboard/activity.html"
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = 'activity'

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        by_day = {}
        for notification in context['activity']:
            day = notification.timestamp.date()
            by_day[day] = by_day.get(day, [])
            by_day[day].append(notification)

        membership = None
        gs = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            gs = GroupSelector(membership)

        context.update({
            "membership": membership,
            "membership_selection": membership_selection,
            "group_selector": gs,
            "activity_by_day": by_day,
        })

        return context

activity = only_for_educator(ActivityView.as_view())

class PrereqInterruptionView(TemplateView):
  template_name = "educators/interruption.html"

  def get_context_data(self, **kwargs):
    presurvey = get_survey(settings.AICHALLENGE_COACH_PRE_SURVEY_ID)
    response = presurvey.response(self.request.user)
    return super().get_context_data( **kwargs, presurvey=response )

prereq_interruption = only_for_educator(PrereqInterruptionView.as_view())

class CoachRemoval(View):
    
  def get(self, request, *args, **kwargs):
    if request.user.educatorprofile.is_coach:
      membership = Membership.objects.get(pk=settings.AICHALLENGE_COACH_MEMBERSHIP_ID)
      member = Member.objects.get(user=request.user, membership=membership)
      member.delete()
      messages.success(self.request,
                       "You are no longer in the AI Family Challenge Coach membership.")
    return HttpResponseRedirect(reverse("educators:home"))

coach_removal = whitelist('coach_removal')(only_for_educator(CoachRemoval.as_view()))