from django.conf import settings
import logging

logger = logging.getLogger(__name__)

__all__ = ['google_analytics']

SESSION_KEY = '_ga_events'

def add_event(request, category, action, label=""):
    if SESSION_KEY not in request.session:
        request.session[SESSION_KEY] = []
    request.session[SESSION_KEY].append({
        'category': category,
        'action': action,
        'label': label
    })

def get_events(request):
    return request.session.pop(SESSION_KEY, [])

def google_analytics(request):
    if not request.user.is_authenticated():
        usertype = "Anonymous"
    elif request.user.is_staff:
        usertype = "Staff"
    else:
        usertype = ""
        if request.user.extra.is_student:
            usertype += "Student"
        if request.user.extra.is_mentor:
            usertype += "Mentor"
        if request.user.extra.is_educator:
            usertype += "Educator"
        if request.user.extra.is_parent:
            usertype += "Parent"

        if not usertype:
            usertype = "Other"
            logger.warn("User categorized as Other for Google Analytics: {}".format(request.user.username))

    userid = None
    if request.user.is_authenticated():
        userid = request.user.id

    free_user = None
    membership_grouping = None
    if request.user.is_authenticated():
        free_user = "Membership" if request.user.extra.in_active_membership else "Free"
        membership_grouping = "-".join([str(id) for id in request.user.membership_set.filter(is_active=True).order_by('id').values_list('id', flat=True)])

    def ga_events():
        return get_events(request)

    return {
        'ga_code': settings.GA_CODE,
        'ga_dimension_user_type': usertype,
        'ga_user_id': userid,
        'ga_dimension_free_user': free_user,
        'ga_membership_grouping': membership_grouping,
        'ga_events': ga_events,
        'gtm_container_id': settings.GTM_CONTAINER_ID,
    }

