from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from .models import Group, Role, Membership
from .forms import GroupJoinForm, GroupLeaveForm
from curiositymachine.decorators import feature_flag
from django.views.decorators.http import require_http_methods
from django.contrib import messages

@feature_flag('enable_groups')
def groups(request):
	groups = Group.objects.all()
	return render(request, 'groups.html', {'groups': groups})

@feature_flag('enable_groups')
def group(request, group_id): 
	group = get_object_or_404(Group, id=group_id)
	return render(request, 'group.html', {'group': group})


@login_required
@feature_flag('enable_groups')
@require_http_methods(["POST"])
def join_group(request):
	group_form = GroupJoinForm(data=request.POST)
	group_form.is_valid()
	group = get_object_or_404(Group, code=group_form.cleaned_data['code'])
	result = group.add_student(request.user)
	if result:
		messages.success(request, 'Successfully subscribed to the %s group' % group.name)
	else:
		messages.error(request, 'Already subscribed to %s group' % group.name)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
@feature_flag('enable_groups')
@require_http_methods(["POST"])
def leave_group(request):
	group_form = GroupLeaveForm(data=request.POST)
	group_form.is_valid()
	group = get_object_or_404(Group, id=group_form.cleaned_data['id'])
	result = group.delete_student(request.user)
	if result:
		messages.success(request, 'Successfully unsubscribed to the %s group' % group.name)
	else:
		messages.error(request, 'Already unsubscribed to %s group' % group.name)
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

# @login_required
# def user_group(request, group_id): 
# 	group = request.user.profile.groups.filter(id=group_id).first()
# 	if not group: return Http404("No group for given query")
# 	return render(request, 'group.html', {'group': group})