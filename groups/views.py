from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Group, Role, Membership, Invitation
from django.contrib.auth.models import User
from .forms import GroupJoinForm, GroupLeaveForm, GroupInviteForm, GroupForm
from . import forms
from curiositymachine.decorators import feature_flag, educator_only, student_only
from .decorators import owners_only
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView
from django.views.generic.edit import DeleteView
from django.views.generic import View
from django.utils.decorators import method_decorator

class GroupListView(ListView):
	model = Group
	context_object_name = 'groups'

	@method_decorator(login_required)
	@method_decorator(educator_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupListView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		return self.request.user.cm_groups.all()

class GroupDetailView(DetailView):
	model = Group
	pk_url_kwarg = 'group_id'

	@method_decorator(login_required)
	@method_decorator(owners_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupDetailView, self).dispatch(*args, **kwargs)

class GroupCreateView(CreateView):
	model = Group
	form_class = GroupForm
	success_url = '/groups/%(id)s'

	@method_decorator(login_required)
	@method_decorator(educator_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupCreateView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		self.object = form.save()
		self.object.add_owner(self.request.user)
		return HttpResponseRedirect(self.get_success_url())

class InvitationCreateView(FormView):
	form_class = forms.MultiInvitationForm
	template_name = 'groups/invitation_form.html'

	@method_decorator(login_required)
	@method_decorator(educator_only)
	def dispatch(self, *args, **kwargs):
		return super(InvitationCreateView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		group = get_object_or_404(Group, id=self.kwargs['group_id'])
		recipients = form.cleaned_data['recipients']
		for user in User.objects.filter(username__in=recipients):
			group.invite_member(user)
		return super(InvitationCreateView, self).form_valid(form)

	def get_success_url(self):
		return reverse('groups:group', kwargs={'group_id': self.kwargs['group_id']})



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
@login_required
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
