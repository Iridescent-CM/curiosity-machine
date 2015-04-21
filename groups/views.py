from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, QueryDict
from django.shortcuts import get_object_or_404, render
from .models import Group, Invitation
from django.contrib.auth.models import User
from . import forms
from curiositymachine.decorators import feature_flag, educator_only, student_only
from .decorators import owners_only
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, FormView, DeleteView, UpdateView
from django.utils.decorators import method_decorator

class GroupDetailView(DetailView):
	model = Group
	pk_url_kwarg = 'group_id'

	@method_decorator(login_required)
	@method_decorator(owners_only)
	@method_decorator(feature_flag('enable_groups'))
	def dispatch(self, *args, **kwargs):
		return super(GroupDetailView, self).dispatch(*args, **kwargs)

class GroupCreateView(CreateView):
	model = Group
	form_class = forms.GroupForm
	success_url = '/groups/%(id)s'

	@method_decorator(login_required)
	@method_decorator(educator_only)
	@method_decorator(feature_flag('enable_groups'))
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
	@method_decorator(owners_only)
	@method_decorator(feature_flag('enable_groups'))
	def dispatch(self, *args, **kwargs):
		query = QueryDict(self.request.META.get('QUERY_STRING'))
		self.is_resend = ('resend' in query)
		self.group = get_object_or_404(Group, id=self.kwargs['group_id'])
		return super(InvitationCreateView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		recipients = form.cleaned_data['recipients']
		for user in User.objects.filter(username__in=recipients):
			self.group.invite_member(user)
		if self.is_resend:
			messages.success(self.request,
				'Resent invitation to %s' % ", ".join(form.cleaned_data['recipients'])
			)
		return super(InvitationCreateView, self).form_valid(form)

	def get_success_url(self):
		return reverse('groups:group', kwargs={'group_id': self.kwargs['group_id']})

	def get_context_data(self, **kwargs):
		context = super(InvitationCreateView, self).get_context_data(**kwargs)
		context.update({'group': self.group})
		return context

class InvitationRejectView(DeleteView):
	model = Invitation
	slug_field = 'group__id'
	slug_url_kwarg = 'group_id'
	success_url = '/home'

	@method_decorator(login_required)
	@method_decorator(feature_flag('enable_groups'))
	def dispatch(self, *args, **kwargs):
		return super(InvitationRejectView, self).dispatch(*args, **kwargs)

	def get_queryset(self):
		return Invitation.objects.filter(user=self.request.user)

class GroupMemberDetailView(DetailView):
	model = User
	pk_url_kwarg = 'user_id'
	template_name = 'groups/member_detail.html'
	context_object_name = 'member'

	@method_decorator(login_required)
	@method_decorator(owners_only)
	@method_decorator(feature_flag('enable_groups'))
	def dispatch(self, *args, **kwargs):
		self.group = get_object_or_404(Group, id=self.kwargs['group_id'])
		return super(GroupMemberDetailView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(GroupMemberDetailView, self).get_context_data(**kwargs)
		context.update({'group': self.group})
		return context

class GroupLeaveView(UpdateView):
	model = Group
	fields = []
	template_name_suffix = '_leave_form'
	pk_url_kwarg = 'group_id'
	success_url = '/home'

	@method_decorator(login_required)
	@method_decorator(student_only)
	def dispatch(self, *args, **kwargs):
		return super(GroupLeaveView, self).dispatch(*args, **kwargs)

	def form_valid(self, form):
		result = self.object.delete_member(self.request.user)
		if result:
			messages.success(self.request, 'You left %s' % self.object.name)
		else:
			messages.error(self.request, 'You already left %s' % self.object.name)
		return super(GroupLeaveView, self).form_valid(form)

@login_required
@feature_flag('enable_groups')
@require_http_methods(["POST"])
@student_only
def join_group(request):
	group_form = forms.GroupJoinForm(data=request.POST)
	if group_form.is_valid():
		group = Group.objects.filter(code=group_form.cleaned_data['code']).first()
		if not group:
			messages.error(request, 'There are no groups with code %s' % group_form.cleaned_data['code'])
		else:
			result = group.add_member(request.user)
			if result:
				messages.success(request, 'You joined %s' % group.name)
			else:
				messages.error(request, 'You are already a member of %s' % group.name)
	else:
		messages.error(request, 'An error occurred, please try again')
	return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@feature_flag('enable_groups')
@login_required
def accept_invitation(request, group_id):
	group = get_object_or_404(Group, id=group_id)
	invitation = Invitation.objects.filter(user=request.user, group=group).first()
	if not invitation:
		return render(request, 'groups/invitation_404.html', status=404)
	invitation.accept()
	messages.success(request, 'You joined %s' % (group.name,))
	return HttpResponseRedirect(reverse('profiles:home'))

class UpdateInvitationsView(UpdateView):
	model = Group
	form_class = forms.ManageInvitationsForm
	template_name = "groups/manage_invitations.html"
	pk_url_kwarg = 'group_id'
	success_url = '/yay'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(UpdateInvitationsView, self).dispatch(*args, **kwargs)

class UpdateMembersView(UpdateView):
	model = Group
	form_class = forms.ManageMembersForm
	template_name = "groups/manage_members.html"
	pk_url_kwarg = 'group_id'
	success_url = '/yay'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		return super(UpdateMembersView, self).dispatch(*args, **kwargs)

