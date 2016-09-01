from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from curiositymachine.decorators import feature_flag, educator_only, student_only
from memberships.models import Membership
from challenges.models import Challenge, Stage
from cmcomments.models import Comment
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from profiles.models import UserRole
from .decorators import members_only

User = get_user_model()

class MembershipDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/membership.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipDetailView, self).dispatch(*args, **kwargs)

class MembershipChallengeListView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/challenges/list.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipChallengeListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        challenges = context["membership"].challenges.select_related('image').all()
        paginator = Paginator(challenges, settings.MD_PAGE_SIZE)
        try:
            challenges = paginator.page(page)
        except PageNotAnInteger:
            challenges = paginator.page(1)
        except EmptyPage:
            challenges = paginator.page(paginator.num_pages)
        context["challenges"]=challenges
        return context

class MembershipChallengeDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/challenges/single.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipChallengeDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        challenge = get_object_or_404(Challenge, pk=self.kwargs.get('challenge_id')) 
        context['challenge'] = challenge

        membership_id = self.kwargs.get('membership_id')
        # TODO: move the query below (or parts of it) somewhere usefully reusable
        progresses = (challenge.progress_set
            .select_related('student__profile', 'mentor')
            .filter(student__membership__id=membership_id)
            .prefetch_related(
                Prefetch(
                    'comments',
                    queryset=Comment.objects.filter(
                        stage=Stage.reflect.value,
                        user__profile__role=UserRole.student.value
                    ),
                    to_attr='student_reflect_comments'
                )
            )
            .order_by("-started")
            .all())

        page = self.request.GET.get('page')
        paginator = Paginator(progresses, settings.MD_PAGE_SIZE)
        try:
            progresses = paginator.page(page)
        except PageNotAnInteger:
            progresses = paginator.page(1)
        except EmptyPage:
            progresses = paginator.page(paginator.num_pages)

        context['progresses'] = progresses

        return context

class MembershipStudentListView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/students/list.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipStudentListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        page = self.request.GET.get('page')

        students = (context["membership"]
            .members
            .select_related('profile')
            .filter(profile__role=UserRole.student.value)
            .all())
        context["students"] = students
        return context

class MembershipStudentDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/students/single.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipStudentDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        return context
