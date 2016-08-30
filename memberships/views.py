from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from curiositymachine.decorators import feature_flag, educator_only, student_only
from memberships.models import Membership
from challenges.models import Challenge
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404

User = get_user_model()

class MembershipDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/membership.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    # TODO: @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipDetailView, self).dispatch(*args, **kwargs)

class MembershipChallengeListView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/challenges/list.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    # TODO: @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipChallengeListView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        challenges = context["membership"].challenges.select_related('image').all()
        paginator = Paginator(challenges, settings.MD_PAGE_SIZE)
        try:
            challenges = paginator.page(page)
        except PageNotAnInteger:
            challenges = paginator.page(1)
        except EmptyPage:
            challenges = paginator.page(paginator.num_pages)
        context["challenges"]=challenges
        return context

class MembershipChallengeDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/challenges/single.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    # TODO: @method_decorator(members_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipChallengeDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)

        challenge = get_object_or_404(Challenge, pk=self.kwargs.get('challenge_id')) 
        context['challenge'] = challenge

        membership_id = self.kwargs.get('membership_id')
        progresses = challenge.progress_set.select_related('student__profile', 'mentor').filter(student__membership__id=membership_id).all()
        context['progresses'] = progresses

        return context
