from profiles.forms import mentor, educator, parent, student
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def login_and_join_forms(request):
    return {
        'login_form': AuthenticationForm(),
        'join_form': student.StudentUserAndProfileForm(prefix="student"),
        'mentor_join_form': mentor.MentorUserAndProfileForm(prefix="mentor"),
        'educator_join_form': educator.EducatorUserAndProfileForm(prefix="educator"),
        'parent_join_form': parent.ParentUserAndProfileForm(prefix="parent")
    }


def google_analytics(request):
    if not request.user.is_authenticated():
        usertype = "Anonymous"
    elif request.user.is_staff:
        usertype = "Staff"
    else:
        usertype = ""
        if request.user.profile.is_student:
            usertype += "Student"
        if request.user.profile.is_mentor:
            usertype += "Mentor"
        if request.user.profile.is_educator:
            usertype += "Educator"
        if request.user.profile.is_parent:
            usertype += "Parent"

        if not usertype:
            usertype = "Other"
            logger.warn("User categorized as Other for Google Analytics: {}".format(request.user.username))

    return {
        'ga_code': settings.GA_CODE,
        'ga_debug': settings.GA_DEBUG,
        'ga_dimension_user_type': usertype
    }

def feature_flags(request):
    return { 'flags': settings.FEATURE_FLAGS }

def template_globals(request):
    return {
        "REQUEST_A_MENTOR_LINK": settings.REQUEST_A_MENTOR_LINK,
        "SITE_MESSAGE": settings.SITE_MESSAGE,
        "SITE_MESSAGE_LEVEL": settings.SITE_MESSAGE_LEVEL
    }
