from allauth.account.forms import LoginForm

def login_form(request):
    return {
        'login_form': LoginForm(),
    }


