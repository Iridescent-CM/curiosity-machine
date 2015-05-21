from profiles.forms import JoinForm, MentorJoinForm, educator
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

def login_and_join_forms(request):
    return {
	'join_form': JoinForm(),
	'login_form': AuthenticationForm(),
	'mentor_join_form': MentorJoinForm(),
	'educator_join_forms': {
	    'userForm': educator.UserCreationForm(prefix="user"),
	    'profileForm': educator.ProfileChangeForm(prefix="profile")
	}
    }


def google_analytics(request):
	return {'ga_code': settings.GA_CODE }

def feature_flags(request):
    return { 'flags': settings.FEATURE_FLAGS }

def template_globals(request):
    return {
        "REQUEST_A_MENTOR_LINK": settings.REQUEST_A_MENTOR_LINK,
        "SITE_MESSAGE": settings.SITE_MESSAGE,
        "SITE_MESSAGE_LEVEL": settings.SITE_MESSAGE_LEVEL
    }
