from challenges.models import Challenge
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from profiles.views import CreateProfileView
from .forms import *
from .models import *

class CreateView(CreateProfileView):
    form_class = NewEducatorProfileForm
    template_name = "educators/educatorprofile_form.html"
    success_url = lazy(reverse, str)("educators:home")

create = CreateView.as_view()

class EditProfileView(UpdateView):
    model = EducatorProfile
    fields = '__all__'

    def get_object(self, queryset=None):
        return self.request.user.educatorprofile

edit = EditProfileView.as_view()

# TODO: move
from datetime import timedelta
from django.conf import settings
from django.utils.timezone import now
class MembershipSelection():
    """
    When given a request, determines if the request user has active memberships
    and which should be considered selected, along with providing some logic helpers.
    """

    session_param = 'active_membership'
    query_param = 'm'

    def __init__(self, request, memberships=None):
        """
        Takes request and optional list of membership dicts. If memberships are passed in, they
        are not queried from the database based on the request user.
        """
        self.request = request

        if memberships is None:
            self.all = self._get_membership_selections_map(request.user)
        else:
            self.all = memberships

        self.selected = None
        if self.all:
            qparam = request.GET.get(self.query_param)
            if qparam:
                try:
                    qparam = int(qparam)
                    self.selected = next(d for d in self.all if d.id == qparam)
                    request.session[self.session_param] = qparam
                except:
                    raise Http404

            elif self.session_param in request.session:
                try:
                    self.selected = next(d for d in self.all if d.id == request.session.get(self.session_param))
                except:
                    del request.session[self.session_param]
                    self.selected = self.all[0]

            else:
                self.selected = self.all[0]

    def _get_membership_selections_map(self, user):
        """
        Gets active membership value dicts for user
        """
        return user.membership_set.filter(is_active=True).order_by('display_name')

    @property
    def count(self):
        # is this needed?
        return len(self.all)

    @property
    def names(self):
        return ", ".join([o.display_name for o in self.all]) or "None"

    @property
    def no_memberships(self):
        # rename to empty?
        return self.count == 0

    @property
    def memberships(self):
        # rename to has_memberships? just use not empty?
        return self.count != 0

    @property
    def recently_expired(self):
        cutoff = now().date() - timedelta(days=settings.MEMBERSHIP_EXPIRED_NOTICE_DAYS)
        return self.request.user.membership_set.expired(cutoff=cutoff)

class HomeView(TemplateView):
    template_name = "educators/dashboard/challenges.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        core_challenges = Challenge.objects.filter(draft=False, core=True).select_related('image').prefetch_related('resource_set')

        membership_challenges = []
        membership = None
        gs = None

        membership_selection = MembershipSelection(self.request)
        if membership_selection.selected:
            membership = membership_selection.selected
            gs = GroupSelector(membership)
            membership_challenges = membership.challenges.select_related('image').prefetch_related('resource_set')
            core_challenges = core_challenges.exclude(id__in=membership_challenges.values('id'))

        context.update({
            "membership": membership,
            "membership_challenges": membership_challenges,
            "core_challenges": core_challenges,
            "membership_selection": membership_selection,
            "group_selector": gs,
        })

        return context

home = HomeView.as_view()
