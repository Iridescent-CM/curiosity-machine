from profiles.forms import MentorJoinForm, educator, parent, student
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

def login_and_join_forms(request):
    return {
        'join_form': student.StudentUserAndProfileForm(),
        'login_form': AuthenticationForm(),
        'mentor_join_form': MentorJoinForm(),
        'educator_join_form': educator.EducatorUserAndProfileForm(prefix="educator"),
        'parent_join_form': parent.ParentUserAndProfileForm(prefix="parent")
    }


def google_analytics(request):
    if not request.user.is_authenticated():
        usertype = "Anonymous"
    else:
        usertype = ""
        if request.user.profile.is_student:
            usertype += "Student"
        if request.user.profile.is_mentor:
            usertype += "Mentor"
        if request.user.profile.is_educator:
            usertype += "Educator"

        if not usertype:
            usertype = "Other"

    return {
        'ga_code': settings.GA_CODE,
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
