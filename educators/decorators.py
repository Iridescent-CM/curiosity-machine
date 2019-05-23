from datetime import timedelta
from django.conf import settings
from django.shortcuts import Http404
from django.template.response import TemplateResponse
from django.utils.timezone import now
from functools import wraps

class MembershipSelection():
    """
    For use in a view decorator. When given a request, determines if the request user has active
    memberships and which should be considered selected, along with providing some logic helpers.
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

    @property
    def challenges_exist(self):
        for membership in self.all:
            num_challenges = membership.challenges.select_related('image').prefetch_related('resource_set').count()
            print("challenges: ", num_challenges)
            if num_challenges > 0:
                return True

def membership_selection(view):
    @wraps(view)
    def inner(request, *args, **kwargs):
        kwargs['membership_selection'] = MembershipSelection(request)
        return view(request, *args, **kwargs)
    return inner


