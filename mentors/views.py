from challenges.models import Progress
from curiositymachine.decorators import whitelist
from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, DateField
from django.db.models.functions import TruncDate
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from profiles.decorators import only_for_role
from profiles.models import UserRole
from profiles.views import EditProfileMixin
from .forms import *

only_for_mentor = only_for_role(UserRole.mentor)
unapproved_ok = whitelist('unapproved_mentors')

class EditView(EditProfileMixin, UpdateView):
    model = MentorProfile
    form_class = MentorProfileForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("mentors:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.mentorprofile

edit = only_for_mentor(
        unapproved_ok(
            EditView.as_view()))

class HomeView(TemplateView):
    template_name = "mentors/home.html"

    def get_context_data(self, **kwargs):
        request = self.request
        context = super().get_context_data(**kwargs)

        startdate = now() - relativedelta(months=int(settings.PROGRESS_MONTH_ACTIVE_LIMIT))
        progresses = Progress.objects.filter(
            mentor=request.user, started__gt=startdate
        ).select_related(
            'challenge',
            'challenge__image',
            'challenge__video',
            'mentor',
            'student',
            'student__profile',
            'student__profile__image'
        ).order_by(
            '-started'
        )[:4]

        unclaimed_days_and_counts = (Progress.objects
            .filter(mentor__isnull=True)
            .exclude(comments=None)
            .annotate(start_day=TruncDate('started'))
            .values_list('start_day')
            .annotate(Count('id'))
            .order_by('-start_day'))

        unclaimed_days = []
        for data in unclaimed_days_and_counts:
            progress = (Progress.objects
                .filter(mentor__isnull=True)
                .exclude(comments=None)
                .annotate(start_day=TruncDate('started'))
                .filter(start_day=data[0])
                .order_by('-started')
                .first())
            unclaimed_days.append((data, progress))

        claimable_progresses = Progress.objects.filter(
            mentor__isnull=True
        ).exclude(
            comments=None
        )
        source_and_counts = claimable_progresses.values('student__extra__source').annotate(count=Count('student__extra__source'))
        partnerships = {
            obj["student__extra__source"]: {
                "source": obj['student__extra__source'],
                "unclaimed": obj['count'],
                "example_progress": claimable_progresses.filter(
                        student__extra__source=obj['student__extra__source']
                    ).select_related(
                        "challenge__image"
                    ).order_by(
                        "-started"
                    ).first()
            } for obj in source_and_counts
        }
        non_partnerships = partnerships.get('', None)
        if non_partnerships:
            del partnerships['']
        partnerships = sorted(partnerships.values(), key=lambda o: o.get('source').lower())

        context.update({
            'progresses': progresses,
            'unclaimed_days': unclaimed_days,
            'progresses_by_partnership': partnerships,
            'non_partnership': non_partnerships
        })
        return context

home = only_for_mentor(
        unapproved_ok(
            HomeView.as_view()))

class ListView(ListView):
    template_name = "mentors/list.html"
    queryset = (MentorProfile.objects
        .filter(user__extra__role=UserRole.mentor.value, user__extra__approved=True)
        .annotate(has_image=Count('image'))
        .select_related('user'))
    ordering = ('-has_image', '-user__date_joined',)
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = 'mentors'

list_all = whitelist('public')(ListView.as_view())

class PublicProfileView(DetailView):
    model = MentorProfile
    slug_field = 'user__username'
    slug_url_kwarg = 'username'
    context_object_name = 'profile'
    template_name = 'mentors/public_profile.html'

    def get_queryset(self):
        return MentorProfile.objects.filter(user__extra__role=UserRole.mentor.value)

public_profile = whitelist('public')(PublicProfileView.as_view())

class ClaimedView(ListView):
    template_name = "mentors/claimed.html"
    ordering = ('-started', 'id')
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = 'progresses'
    extra_context = {
        'claimed': True
    }

    def get_queryset(self):
        self.queryset = (Progress.objects
            .filter(mentor=self.request.user)
            .select_related(
                'challenge', 'mentor', 'student', 'student__profile',
                'student__profile__image', 'challenge__image'))
        return super().get_queryset()

claimed = only_for_mentor(ClaimedView.as_view())

class UnclaimedBySourceView(ListView):
    template_name = "mentors/unclaimed.html"
    ordering = "-started"
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = "progresses"

    def get_queryset(self):
        self.queryset = (Progress.objects
            .filter(mentor__isnull=True, student__extra__source=self.request.GET['source'])
            .exclude(comments=None)
            .select_related(
                'challenge', 'student', 'student__profile',
                'student__profile__image', 'challenge__image'))
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        grouping = self.request.GET['source']
        if grouping == '':
            grouping = "other"
        return super().get_context_data(
            grouping=grouping,
            **kwargs
        )

unclaimed_by_source = only_for_mentor(UnclaimedBySourceView.as_view())

class UnclaimedByDateView(ListView):
    template_name = "mentors/unclaimed.html"
    ordering = "-started"
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = "progresses"

    def dispatch(self, request, *args, **kwargs):
        self.selected_date = date(
            int(self.kwargs['year']),
            int(self.kwargs['month']),
            int(self.kwargs['day'])
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.queryset = (Progress.objects
            .filter(mentor__isnull=True)
            .annotate(start_day=TruncDate('started'))
            .filter(start_day=self.selected_date)
            .exclude(comments=None)
            .select_related(
                'challenge', 'student', 'student__profile',
                'student__profile__image', 'challenge__image'))
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            grouping=self.selected_date,
            **kwargs
        )

unclaimed_by_date = only_for_mentor(UnclaimedByDateView.as_view())
