from django.contrib.auth.decorators import login_required
from django.http import Http404
import password_reset.views
import password_reset.forms

from . import student
from . import mentor
from . import educator
from . import staff

@login_required
def dispatch(request, action):
    if request.user.profile.is_mentor:
        module = mentor
    elif request.user.profile.is_student:
        module = student
    elif request.user.profile.is_educator:
        module = educator
    elif request.user.is_staff:
        module = staff
    else:
        raise Http404()

    fn = getattr(module, action, None)
    if fn:
        return fn(request)
    else:
        raise Http404()

### password recovery

class Recover(password_reset.views.Recover):
    search_fields = ['username'] # search only on username, not on email. this is important because email is not a unique field in this app!

recover = Recover.as_view()
