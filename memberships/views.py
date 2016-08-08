from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from curiositymachine.decorators import feature_flag, educator_only, student_only
from memberships.models import Membership
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

class MembershipDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/educator/membership.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipDetailView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        paginator = Paginator(context["membership"].challenges.all(), settings.MD_PAGE_SIZE)
        try:
            challenges = paginator.page(page)
        except PageNotAnInteger:
            challenges = paginator.page(1)
        except EmptyPage:
            challenges = paginator.page(paginator.num_pages)
        context["challenges"]=challenges
        return context

class MembershipDesignChallengeView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/educator/design-challenges.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipDesignChallengeView, self).dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context=super().get_context_data(**kwargs)
        page = self.request.GET.get('page')
        paginator = Paginator(context["membership"].challenges.all(), settings.MD_PAGE_SIZE)
        try:
            challenges = paginator.page(page)
        except PageNotAnInteger:
            challenges = paginator.page(1)
        except EmptyPage:
            challenges = paginator.page(paginator.num_pages)
        context["challenges"]=challenges
        return context

# the view below needs to include the DC info in it
class MembershipStudentProgressView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/educator/design-challenge-individual.html'
    context_object_name = 'membership'

# the view below needs to include the Student info in it
class MembershipStudentsView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/educator/students.html'
    context_object_name = 'membership'

# the view below needs to include the DC info in it
# class MembershipStudentIndividualView(DetailView):
#     model = Membership
#     pk_url_kwarg = 'membership_id'
#     template_name = 'memberships/educator/student-individual.html'
#     context_object_name = 'membership'
