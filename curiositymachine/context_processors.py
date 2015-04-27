from profiles.forms import JoinForm,MentorJoinForm
from django.contrib.auth.forms import AuthenticationForm
from django.conf import settings

def login_and_join_forms(request):
    return {'join_form': JoinForm(), 'login_form': AuthenticationForm(), 'mentor_join_form': MentorJoinForm()}


def google_analytics(request):
	return {'ga_code': settings.GA_CODE }

def feature_flags(request):
    return { 'flags': settings.FEATURE_FLAGS }

def template_globals(request):
    return {
	"REQUEST_A_MENTOR_LINK": settings.REQUEST_A_MENTOR_LINK
    }
