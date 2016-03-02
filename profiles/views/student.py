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
from curiositymachine.views.generic import ToggleView, SoftDeleteView, UserJoinView
from django.db import transaction
from django.views.generic.edit import UpdateView
from django.utils.functional import lazy
from django.utils.decorators import method_decorator
from profiles.decorators import connected_child_only
from curiositymachine.decorators import feature_flag

class StudentUserJoinView(UserJoinView):
    def get_success_url(self):
        if self.object.profile.is_underage():
            return reverse('profiles:underage_student')
        else:
            return '/'

join = transaction.atomic(StudentUserJoinView.as_view(
    form_class = StudentUserAndProfileForm,
    prefix = 'student',
    logged_in_redirect = lazy(reverse, str)('profiles:home')
))

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
def dashboard(request):
    filter = request.GET.get('filter')
    my_challenges_filters = [ 'active', 'completed', 'all' ]
    favorite_challenges = Favorite.objects.filter(student=request.user)
    progresses = Progress.objects.filter(student=request.user).select_related("challenge")
    completed_progresses = [progress for progress in progresses if progress.completed]
    active_progresses = [progress for progress in progresses if not progress.completed]
    connections = ParentConnection.objects.filter(child_profile=request.user.profile, removed=False)
    return render(request, "profiles/student/dashboard.html", {
        'active_progresses': active_progresses,
        'completed_progresses': completed_progresses,
        'progresses': progresses,
        'filter': filter,
        'my_challenges_filters': my_challenges_filters,
        'favorite_challenges': favorite_challenges,
        'group_form': GroupJoinForm(),
        'groups': request.user.cm_groups.all(),
        'invitations': Invitation.objects.filter(user=request.user).all(),
        'parent_connections': connections,
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
    return render(request, 'profiles/underage_student.html')

def reverse_with_anchor(view, anchor):
    return "{}#{}".format(reverse(view), anchor)

class ParentConnectionDeleteView(SoftDeleteView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    template_name = 'profiles/student/parentconnection_confirm_delete.html'
    success_url = lazy(reverse_with_anchor, str)('profiles:home', 'parents')
    deletion_field = 'removed'

    @method_decorator(login_required)
    @method_decorator(connected_child_only)
    def dispatch(self, *args, **kwargs):
            return super(ParentConnectionDeleteView, self).dispatch(*args, **kwargs)

remove_connection = ParentConnectionDeleteView.as_view()

class ParentConnectionToggleView(ToggleView):
    model = ParentConnection
    pk_url_kwarg = 'connection_id'
    success_url = lazy(reverse_with_anchor, str)('profiles:home', 'parents')

    @method_decorator(login_required)
    @method_decorator(connected_child_only)
    def dispatch(self, *args, **kwargs):
            return super(ParentConnectionToggleView, self).dispatch(*args, **kwargs)

    def toggle(self, obj):
        obj.active = not obj.active
        obj.save(update_fields=['active'])
        if obj.active:
            messages.success(self.request, "{} can now see your progress".format(obj.parent_profile.user.username))
        else:
            messages.success(self.request, "{} can no longer see your progress".format(obj.parent_profile.user.username))
