from django.utils.functional import wraps
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def mentor_or_current_student(view):
    @wraps(view)
    def inner(request, challenge_id, username, *args, **kwargs):
        if request.user.profile.is_mentor or request.user.username == username: 
            return view(request, challenge_id, username, *args, **kwargs)
        return HttpResponseRedirect(reverse('challenges:challenge', kwargs={'challenge_id': challenge_id}))
    return inner
