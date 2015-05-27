from django.shortcuts import render
from django.contrib import auth, messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.db import IntegrityError
from django.forms.util import ErrorList
from django.core.urlresolvers import reverse
from profiles.forms.student import StudentUserAndProfileForm
from groups.forms import GroupJoinForm, GroupLeaveForm
from groups.models import Invitation
from challenges.models import Progress, Favorite
from profiles.models import ParentConnection
from curiositymachine.views.generic import ToggleView, SoftDeleteView
from django.db import transaction
from django.views.generic.edit import UpdateView
from django.utils.functional import lazy
from django.utils.decorators import method_decorator
from profiles.decorators import connected_child_only

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
    connections = ParentConnection.objects.filter(child_profile=request.user.profile, removed=False)
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
        'parent_connections': connections
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

class ParentConnectionDeleteView(SoftDeleteView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    template_name = 'profiles/student/parentconnection_confirm_delete.html'
    success_url = lazy(reverse, str)('profiles:home')
    deletion_field = 'removed'

    @method_decorator(login_required)
    @method_decorator(connected_child_only)
    def dispatch(self, *args, **kwargs):
            return super(ParentConnectionDeleteView, self).dispatch(*args, **kwargs)

remove_connection = ParentConnectionDeleteView.as_view()

class ParentConnectionToggleView(ToggleView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    success_url = lazy(reverse, str)('profiles:home')

    @method_decorator(login_required)
    @method_decorator(connected_child_only)
    def dispatch(self, *args, **kwargs):
            return super(ParentConnectionToggleView, self).dispatch(*args, **kwargs)

    def toggle(self, obj):
        obj.active = not obj.active
        obj.save(update_fields=['active'])
