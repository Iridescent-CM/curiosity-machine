from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from .models import Group, Role, Membership, Invitation
from django.contrib.auth.models import User
from .forms import GroupJoinForm, GroupLeaveForm, GroupInviteForm, GroupForm
from curiositymachine.decorators import feature_flag, educator_only, student_only
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.utils.decorators import method_decorator

class GroupListView(ListView):
	model = Group

	@method_decorator(login_required)
	@method_decorator(educator_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupListView, self).dispatch(*args, **kwargs)

class GroupDetailView(DetailView):
	model = Group
	pk_url_kwarg = 'group_id'

	@method_decorator(login_required)
	@method_decorator(educator_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupDetailView, self).dispatch(*args, **kwargs)

class GroupCreateView(CreateView):
	model = Group
	form_class = GroupForm
	success_url = '/challenges'

	@method_decorator(login_required)
	@method_decorator(educator_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupCreateView, self).dispatch(*args, **kwargs)

@feature_flag('enable_groups')
@educator_only
def groups(request):
	groups = Group.objects.all()
	return render(request, 'groups.html', {'groups': groups})

@feature_flag('enable_groups')
@educator_only
def group(request, group_id): 
	invite_form = GroupInviteForm(data=request.POST)
	group = get_object_or_404(Group, id=group_id)
	return render(request, 'group.html', {'group': group, 'invite_form': invite_form})

@feature_flag('enable_groups')
@feature_flag('enable_educators')
@require_http_methods(["POST"])
@educator_only
def create(request):
	form = GroupForm(data=request.POST)
	if form.is_valid():
		group = Group.objects.create(name=form.cleaned_data['name'])
		group.add_owner(request.user)
		messages.success(request, 'Successfully created the %s group' % group.name)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
	
@login_required
@feature_flag('enable_groups')
@require_http_methods(["POST"])
@student_only
def join_group(request):
	group_form = GroupJoinForm(data=request.POST)
	if group_form.is_valid():
		group = get_object_or_404(Group, code=group_form.cleaned_data['code'])
		result = group.add_member(request.user)
		if result:
			messages.success(request, 'Successfully subscribed to the %s group' % group.name)
		else:
			messages.error(request, 'You are already a member of %s' % group.name)
	else:
		messages.error(request, 'Invalid code')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@feature_flag('enable_groups')
@require_http_methods(["POST"])
@student_only
def leave_group(request):
	group_form = GroupLeaveForm(data=request.POST)
	group_form.is_valid()
	group = get_object_or_404(Group, id=group_form.cleaned_data['id'])
	result = group.delete_member(request.user)
	if result:
		messages.success(request, 'Successfully unsubscribed to the %s group' % group.name)
	else:
		messages.error(request, 'Already unsubscribed to %s group' % group.name)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


@login_required
@feature_flag('enable_groups')
@feature_flag('enable_educators')
@require_http_methods(["POST"])
@educator_only
def invite_to_group(request, group_id):
	invite_form = GroupInviteForm(data=request.POST)
	if invite_form.is_valid():
		group = get_object_or_404(Group, id=group_id)
		try:
			user = User.objects.get(Q(email=invite_form.cleaned_data['email']) | Q(username=invite_form.cleaned_data['email']))
			group.invite_member(user)
			messages.success(request, 'Successfully invited %s to %s group' % (invite_form.cleaned_data['email'],group.name,))
		except User.DoesNotExist:
			messages.error(request, 'User %s not found' % (invite_form.cleaned_data['email'],))
	else:
		messages.error(request, 'Invalid invitation username or email')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@feature_flag('enable_groups')
@student_only
def accept_invitation(request, group_id):
	group = get_object_or_404(Group, id=group_id)
	invitation = Invitation.objects.filter(user=request.user, group=group).first()
	try:
		user = group.accept_invitation(invitation)
		messages.success(request, 'Successfully joined %s group' % (group.name,))
	except User.DoesNotExist:
		raise Http404("User not found for specified token. This invitation might have expired.")
	
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('profiles:home'))
	else:
		return HttpResponseRedirect(reverse('challenges:challenges'))

from django.views.generic.edit import CreateView
from groups.models import Group

class GroupCreate(CreateView):
	model = Group
	fields = ['name']

	def dispatch(self, request, *args, **kwargs):
		redirect_to = request.POST.get('next', request.GET.get('next', request.META.get('HTTP_REFERER')))
		if not is_safe_url(url=redirect_to, host=request.get_host()):
			redirect_to = resolve_url('/')
		self.redirect_to = redirect_to
		return super(GroupCreate, self).dispatch(request, args, kwargs)

	def get_context_data(self, **kwargs):
		data = super(GroupCreate, self).get_context_data(**kwargs)
		data.update({'redirect_to': self.redirect_to})
		return data

	def get_success_url(self, *args, **kwargs):
		return self.redirect_to
