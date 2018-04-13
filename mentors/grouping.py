from challenges.models import Progress
from django.db.models import Count
from django.db.models.functions import TruncDay
from django.urls import reverse

class ProgressGroup:
    def __init__(self, *args, **kwargs):
        for attr in ['url', 'image_url', 'title', 'unclaimed']:
            setattr(self, attr, kwargs.pop(attr))

class DateGrouper:
    def group(self, *args, **kwargs):
        startdate = kwargs.pop('startdate')
        unclaimed_days_and_counts = (Progress.objects
            .filter(mentor__isnull=True, started__gt=startdate)
            .exclude(comments=None)
            .annotate(start_day=TruncDay('started'))
            .values_list('start_day')
            .annotate(Count('id'))
            .order_by('-start_day'))

        date_groups = []
        for data in unclaimed_days_and_counts:
            progress = (Progress.objects
                .filter(mentor__isnull=True)
                .exclude(comments=None)
                .annotate(start_day=TruncDay('started'))
                .filter(start_day__date=data[0])
                .order_by('-started')
                .first())
            date_groups.append(ProgressGroup(
                url=reverse(
                    "mentors:unclaimed_progresses",
                    kwargs={
                        "year": data[0].year,
                        "month": data[0].month,
                        "day": data[0].day,
                    }
                ),
                image_url=progress.challenge.image.url, # TODO: fallback?
                title=data[0].date().strftime("%B %d, %Y"),
                unclaimed=data[1],
            ))

        return date_groups

class SourceGrouper:
    def group(self, *args, **kwargs):
        startdate = kwargs.pop('startdate')
        claimable_progresses = Progress.objects.filter(
            mentor__isnull=True, started__gt=startdate
        ).exclude(
            comments=None
        )
        source_and_counts = claimable_progresses.values('owner__extra__source').annotate(count=Count('owner__extra__source'))

        source_groups = []
        nonsource = None
        for obj in source_and_counts:
            source = obj['owner__extra__source']
            progress = claimable_progresses.filter(
                owner__extra__source=source
            ).select_related(
                "challenge__image"
            ).order_by(
                "-started"
            ).first()
            url = reverse("mentors:unclaimed_progresses_base") + "?source=%s" % source
            
            group = ProgressGroup(
                url=url,
                image_url=progress.challenge.image.url, # TODO: fallback?
                title=source or "Other",
                unclaimed=obj['count'],
            )
            if source:
                source_groups.append(group)
            else:
                nonsource = group
        
        ordered = sorted(source_groups, key=lambda o: o.title.lower())
        if nonsource:
            ordered.append(nonsource)
        return ordered

