from django.shortcuts import render
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, Http404
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.forms.student import StudentUserAndProfileForm
from groups.forms import GroupJoinForm, GroupLeaveForm
from groups.models import Invitation
from challenges.models import Progress, Favorite
from profiles.models import ParentConnection
from django.db import transaction
from django.views.generic.edit import DeleteView, UpdateView
from django.utils.functional import lazy

@transaction.atomic
def join(request):
    if request.method == 'POST':
        form = StudentUserAndProfileForm(data=request.POST)
        if form.is_valid():
            user = form.save()
            user = auth.authenticate(username=form.cleaned_data['username'], password=form.cleaned_data['password'])
            auth.login(request, user)
            user.profile.deliver_welcome_email()
            return HttpResponseRedirect('/')
        else:
            return render(request, 'join.html', {'form': form,})
    else:
        if request.user.is_authenticated():
            return HttpResponseRedirect(reverse('profiles:home'))
        form = StudentUserAndProfileForm()

    return render(request, 'join.html', {'form': form,})

@login_required
def home(request):
    filter = request.GET.get('filter')
    my_challenges_filters = [ 'active', 'completed', 'all' ]
    favorite_challenges = Favorite.objects.filter(student=request.user)
    progresses = Progress.objects.filter(student=request.user).select_related("challenge")
    completed_progresses = [progress for progress in progresses if progress.completed]
    active_progresses = [progress for progress in progresses if not progress.completed]
    return render(request, "profiles/student/home.html", {
        'active_progresses': active_progresses, 
        'completed_progresses': completed_progresses, 
        'progresses': progresses, 
        'filter': filter, 
        'my_challenges_filters': my_challenges_filters, 
        'favorite_challenges': favorite_challenges,
        'group_form': GroupJoinForm(),
        'groups': request.user.cm_groups.all(),
        'invitations': Invitation.objects.filter(user=request.user).all(),
        'parent_connections': request.user.profile.connections_as_child.all(),
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = StudentUserAndProfileForm(data=request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile has been updated.')
        else:
            messages.error(request, 'Correct errors below.')
    else:
        form = StudentUserAndProfileForm(instance=request.user)

    return render(request, 'profile_edit.html', {'form': form,})

def underage(request):
    return render(request, 'underage_student.html')

class ParentConnectionDeleteView(DeleteView):
    pass

from django.core.exceptions import ImproperlyConfigured
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.base import View
from django.utils.encoding import force_text

class ToggleView(SingleObjectMixin, View):

    def get(self, request, *args, **kwargs):
        raise Http404()

    def post(self, request, *args, **kwargs):
        obj = self.get_object()
        self.toggle(obj)
        return HttpResponseRedirect(force_text(self.success_url))

    def toggle(self, obj):
        raise ImproperlyConfigured("You must override toggle")

class ParentConnectionToggleView(ToggleView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    success_url = lazy(reverse, str)('profiles:home')

    def toggle(self, obj):
        obj.active = not obj.active
        obj.save(update_fields=['active'])
