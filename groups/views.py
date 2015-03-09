from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Group, Role, Membership
from django.contrib.auth.models import User
from .forms import GroupJoinForm, GroupLeaveForm, GroupInviteForm, GroupForm
from curiositymachine.decorators import feature_flag, educator_only, student_only
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Q

@feature_flag('enable_groups')
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
def accept_invitation(request, group_id, token):
	group = get_object_or_404(Group, id=group_id)
	try:
		user = group.accept_invitation(token)
		messages.success(request, 'Successfully joined %s group' % (group.name,))
	except User.DoesNotExist:
		raise Http404("User not found for specified token. This invitation might have expired.")
	
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('profiles:home'))
	else:
		return HttpResponseRedirect(reverse('challenges:challenges'))
