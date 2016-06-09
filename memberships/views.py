from django.views.generic.detail import DetailView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from curiositymachine.decorators import feature_flag, educator_only, student_only
from memberships.models import Membership

class MembershipDetailView(DetailView):
    model = Membership
    pk_url_kwarg = 'membership_id'
    template_name = 'memberships/membership.html'
    context_object_name = 'membership'

    @method_decorator(login_required)
    @method_decorator(educator_only)
    def dispatch(self, *args, **kwargs):
        return super(MembershipDetailView, self).dispatch(*args, **kwargs)
