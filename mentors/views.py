from challenges.models import Progress
from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db.models import Count
from django.utils.timezone import now
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from .forms import *

class EditProfileView(UpdateView):
    model = MentorProfile
    fields = '__all__'

    def get_object(self, queryset=None):
        return self.request.user.mentorprofile

edit = EditProfileView.as_view()

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

        unclaimed_days = [(day, Progress.unclaimed(day[0])[0]) for day in Progress.unclaimed_days()]

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

home = HomeView.as_view()
