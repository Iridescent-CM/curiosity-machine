from profiles.forms import JoinForm
from django.contrib.auth.forms import AuthenticationForm

def login_and_join_forms(request):
        return {'join_form': JoinForm(), 'login_form': AuthenticationForm(),}
