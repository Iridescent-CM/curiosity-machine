from allauth.account.models import EmailAddress
from challenges.models import Progress, Favorite, Challenge
from challenges.presenters import ChallengeSet
from curiositymachine.decorators import unapproved_only
from django.conf import settings
from django.contrib import messages
from django.shortcuts import Http404, get_object_or_404
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, FormView, ListView, TemplateView, UpdateView
from parents.models import ParentConnection
from profiles.decorators import only_for_role, UserRole
from profiles.views import EditProfileMixin
from .forms import *
from .models import StudentProfile

only_for_student = only_for_role(UserRole.student)

def banner_membership_blacklisted(request):
    membership_set = request.user.membership_set.filter(is_active=True)
    return any(membership.id in settings.AI_BANNER_STUDENT_BLACKLIST for membership in membership_set)


class CreateView(EditProfileMixin, CreateView):
    model = StudentProfile
    form_class = NewStudentProfileForm

    def get_success_url(self):
        if self.object.is_underage():
            return reverse("students:underage")
        return reverse("challenges:challenges")

create = only_for_role(UserRole.none)(CreateView.as_view())

class EditView(EditProfileMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileEditForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("students:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.studentprofile

edit = only_for_student(EditView.as_view())

class DashboardMixin:
    def get_context_data(self, **kwargs):
        memberships = self.request.user.membership_set.filter(is_active=True).order_by('display_name')
        names = ", ".join([m.display_name for m in memberships])
        return super().get_context_data(
            **kwargs,
            memberships=memberships,
            membership_names=names,
            banner_membership_blacklisted=banner_membership_blacklisted(self.request),
        )

class ChallengesView(DashboardMixin, ListView):
    template_name = "students/dashboard/challenges/my_challenges.html"
    paginate_by = settings.DEFAULT_PER_PAGE

    def get_queryset(self):
        return (Progress.objects
            .filter(owner=self.request.user)
            .select_related("challenge", "challenge__image")
            .order_by('-started')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        progresses = context.pop('object_list')
        presenter = ChallengeSet([p.challenge for p in progresses], progresses)
        context['object_list'] = context['challenges'] = presenter.challenges
        return context

home = only_for_student(ChallengesView.as_view())

class MembershipChallengesView(DashboardMixin, TemplateView):
    template_name = "students/dashboard/challenges/membership.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        m_id = kwargs.get('membership_id')
        membership = get_object_or_404(self.request.user.membership_set.filter(is_active=True), id=m_id)

        challenges = (membership.challenges
            .select_related("image")
            .all()
        )
        progresses = Progress.objects.filter(owner=self.request.user, challenge_id__in=[c.id for c in challenges])
        presenter = ChallengeSet(challenges, progresses)

        context['challenges'] = presenter.challenges
        return context

membership_challenges = only_for_student(MembershipChallengesView.as_view())

class FavoritesView(DashboardMixin, ListView):
    template_name = "students/dashboard/challenges/favorites.html"
    paginate_by = settings.DEFAULT_PER_PAGE

    def get_queryset(self):
        return (Favorite.objects
            .select_related("challenge", "challenge__image")
            .filter(student=self.request.user)
            .order_by('-id')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        favs = context.pop('object_list')
        challenges = [f.challenge for f in favs]
        progresses = Progress.objects.filter(owner=self.request.user, challenge_id__in=[c.id for c in challenges])
        presenter = ChallengeSet(challenges, progresses)
        context['challenges'] = context['object_list'] = presenter.challenges
        return context

favorites = only_for_student(FavoritesView.as_view())

underage = unapproved_only(TemplateView.as_view(template_name='students/underage.html'))
