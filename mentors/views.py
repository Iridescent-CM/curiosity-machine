from challenges.models import Progress
from curiositymachine.decorators import whitelist
from datetime import date
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, DateField
from django.db.models.functions import TruncDate
from django.http import Http404
from django.urls import reverse
from django.utils.timezone import now
from django.views.generic import TemplateView, UpdateView, DetailView, ListView
from profiles.decorators import only_for_role
from profiles.models import UserRole
from profiles.views import EditProfileMixin
from .forms import *
from .grouping import *

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
            mentor=request.user,
        ).select_related(
            'challenge',
            'challenge__image',
            'challenge__video',
            'mentor',
            'owner',
        ).order_by(
            '-started'
        )[:4]

        context.update({
            'progresses': progresses,
            'date_groups': DateGrouper().group(startdate=startdate)[:8],
            'source_groups': SourceGrouper().group(startdate=startdate)[:8],
        })
        return context

home = only_for_mentor(
        unapproved_ok(
            HomeView.as_view()))

class GroupView(ListView):
    template_name = "mentors/progress_groups.html"
    paginate_by = None
    context_object_name = 'groups'

    def get(self, request, *args, **kwargs):
        self.group_by = self.request.GET.get('by')
        if self.group_by not in ['date', 'source']:
            raise Http404
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        # we're going to cheat and return arrays
        startdate = now() - relativedelta(months=int(settings.PROGRESS_MONTH_ACTIVE_LIMIT))
        if self.group_by == 'date':
            return DateGrouper().group(startdate=startdate)
        elif self.group_by == 'source':
            return SourceGrouper().group(startdate=startdate)
        else:
            raise Http404

    def get_context_data(self, **kwargs):
        group_name = ""
        if self.group_by == "date":
            group_name = "Date"
        elif self.group_by == "source":
            group_name = "Partnership"

        return super().get_context_data(
            **kwargs,
            group=group_name
        )

unclaimed_groups = only_for_mentor(GroupView.as_view())
    
class ListView(ListView):
    template_name = "mentors/list.html"
    queryset = (MentorProfile.objects
        .filter(full_access=True)
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
                'challenge', 'mentor', 'owner',
                'challenge__image'))
        return super().get_queryset()

claimed = only_for_mentor(ClaimedView.as_view())

class UnclaimedBySourceView(ListView):
    template_name = "mentors/unclaimed.html"
    ordering = "-started"
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = "progresses"

    def get_queryset(self):
        if 'source' not in self.request.GET:
            raise Http404
        startdate = now() - relativedelta(months=int(settings.PROGRESS_MONTH_ACTIVE_LIMIT))
        self.queryset = (Progress.objects
            .filter(mentor__isnull=True, owner__extra__source=self.request.GET['source'], started__gt=startdate)
            .exclude(comments=None)
            .select_related(
                'challenge', 'owner',
                'challenge__image'))
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
                'challenge', 'owner',
                'challenge__image'))
        return super().get_queryset()

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            grouping=self.selected_date,
            **kwargs
        )

unclaimed_by_date = only_for_mentor(UnclaimedByDateView.as_view())
