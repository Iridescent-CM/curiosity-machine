from django.contrib.auth.decorators import login_required
from django.http import Http404
import password_reset.views
import password_reset.forms

from . import student
from . import mentor

@login_required
def dispatch(request, action):
    if request.user.profile.is_mentor:
        module = mentor
    else:
        module = student
    fn = getattr(module, action, None)
    if fn:
        return fn(request)
    else:
        raise Http404()

### password recovery

class Recover(password_reset.views.Recover):
    search_fields = ['username'] # search only on username, not on email. this is important because email is not a unique field in this app!

recover = Recover.as_view()
