from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, reverse
from families.aichallenge import get_stages
from memberships.models import Membership
from urllib.parse import quote_plus
from .models import *

def _get_int_or_404(params, key):
    value = params.get(key)
    try:
        value = int(value)
    except ValueError:
        raise Http404
    return value

class FilterSet():
    query_param = None

    def __init__(self, request=None):
        self.request = request
        self.response = None
        self.applied = None
        self.active = None

    @property
    def requested(self):
        if not hasattr(self, "query_param"):
            return False
        else:
            return self.query_param in self.request.GET

    def apply(self):
        pass

    def get_template_contexts():
        pass

class UnfilteredChallenges(FilterSet):

    @property
    def requested(self):
        return False

    def apply(self):
        self.applied = True
        return None, {
            "title": "All Design Challenges",
            "challenges": Challenge.objects
        }, None

    def get_template_contexts(self):
        return [{
            "text": "All Challenges",
            "full_url": reverse("challenges:challenges") + "#challenges",
            "active": bool(self.applied)
        }]

class CoreChallenges(FilterSet):
    query_param = "aifamilychallenge"

    def apply(self):
        self.applied = True
        return None, {
            "title": "AI Family Challenge",
            "challenges": Challenge.objects.filter(core=True),
        }, None

    def get_template_contexts(self):
        if Challenge.objects.filter(core=True, draft=False).count() > 0:
            return [{
                "text": "AI Family Challenge",
                "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, 1),
                "active": bool(self.applied)
            }]
        else:
            return []

class MembershipChallenges(FilterSet):
    query_param = "membership"

    def apply(self):
        membership_id = _get_int_or_404(self.request.GET, self.query_param)

        if not self.request.user.is_authenticated():
            return None, None, HttpResponseRedirect('%s?next=%s' % (reverse('login'), quote_plus(self.request.get_full_path())))

        membership = Membership.objects.filter(id=membership_id, members=self.request.user, is_active=True).first()
        if not membership:
            messages.error(self.request, "Oops! You are not part of that membership.")
            return None, None, redirect("challenges:challenges")

        self.applied = membership_id
        return None, {
            "title": membership.display_name + " Design Challenges",
            "challenges": membership.challenges
        }, None

    def get_template_contexts(self):
        user_memberships = []
        if self.request.user.is_authenticated():
            user_memberships = self.request.user.membership_set.filter(is_active=True)

        return [{
            "text": membership.display_name,
            "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, membership.id),
            "active": membership.id == self.applied
        } for membership in user_memberships]

class AIFCChallenges(FilterSet):
    query_param = "aifamilychallenge"

    def apply(self):
        self.applied = True
        return "challenges/aifc.html", {
            "title": "AI Family Challenge",
            "stages": get_stages(),
            "header_template": "challenges/filters/free.html",
        }, None

    def get_template_contexts(self):
        if Challenge.objects.filter(core=True, draft=False).count() > 0:
            return [{
                "text": "AI Family Challenge",
                "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, 1),
                "active": bool(self.applied)
            }]
        else:
            return []

class FilterChallenges(FilterSet):
    query_param = "filter_id"

    def apply(self):
        filter_id = _get_int_or_404(self.request.GET, self.query_param)
        self.active = get_object_or_404(Filter.objects.filter(visible=True), id=filter_id)

        self.applied = filter_id
        return None, {
            "title": self.active.name + " Design Challenges",
            "challenges": self.active.challenges,
            "header_template": self.active.header_template,
        }, None

    def get_template_contexts(self):
        filters = Filter.objects.filter(visible=True).prefetch_related('challenges__image')
        return [{
            "text": f.name,
            "full_url": reverse("challenges:challenges") + "?%s=%d#challenges" % (self.query_param, f.id),
            "active": f.id == self.applied
        } for f in filters]

class ThemeChallenges(FilterSet):
    query_param = "theme"

    def apply(self):
        theme_name = self.request.GET.get(self.query_param)
        self.applied = theme_name
        return None, {
            "title": theme_name + " Design Challenges",
            "challenges": Challenge.objects.filter(themes__name=theme_name)
        }, None

    def get_template_contexts(self):
        return [{
            "text": '<i class="icon %s"></i> %s' % (theme.icon, theme.name),
            "full_url": reverse("challenges:challenges") + "?%s=%s#challenges" % (self.query_param, theme.name),
            "active": theme.name == self.applied
        } for theme in Theme.objects.all()]

