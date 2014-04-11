from datetime import datetime
from datetime import timedelta
from django.utils.timezone import now
from django.utils.timesince import timesince

from django import template
register = template.Library()

@register.filter(name="timesince", is_safe=False)
def timesince_filter(value):
    """Formats a date as the time since that date (i.e. "4 mins ago")."""
    if not value:
        return ''
    try:
        td = timedelta(days=1)
        right_now = now()
        if value > right_now - td:
            ts = timesince(value)
            if ts:
                if ',' in ts:
                    ts = ts.split(',')[0]
                ts = '%s ago' % ts
        elif value > right_now - timedelta(days=2):
            ts = 'Yesterday'
        elif value > right_now - timedelta(days=7):
            ts = 'Last %s' % value.strftime('%A')
        else:
            ts = value.strftime('%m.%d.%y')
        return ts
    except (ValueError, TypeError):
        return ''