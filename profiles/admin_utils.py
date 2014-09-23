from django.contrib import admin
from datetime import date
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _

class StudentFilter(admin.SimpleListFilter):
    # Human-readable title which will be displayed in the
    # right admin sidebar just above the filter options.
    title = _('Age Category')

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'age_category'

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples. The first element in each
        tuple is the coded value for the option that will
        appear in the URL query. The second element is the
        human-readable name for the option that will appear
        in the right sidebar.
        """
        return (
            ('13plus', _('above thirteen')),
            ('underage', _('below thirteen')),
        )

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        # Compare the requested value (either '80s' or '90s')
        # to decide how to filter the queryset.
        n = now()
        thirteen_years_ago = date(n.year - 13, n.month, n.day)
        queryset.filter(profile__birthday__isnull=False)
        if self.value() == 'underage':
            return queryset.filter(profile__birthday__gte=thirteen_years_ago)
        if self.value() == '13plus':
            return queryset.filter(profile__birthday__lt=thirteen_years_ago)