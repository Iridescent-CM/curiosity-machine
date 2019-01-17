from allauth.account.models import EmailAddress
from challenges.models import Progress, Favorite, Challenge
from curiositymachine.decorators import unapproved_only, whitelist
from curiositymachine.presenters import LearningSet
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import Http404, get_object_or_404
from django.urls import reverse
from django.utils.functional import lazy
from django.views.generic import CreateView, FormView, ListView, RedirectView, TemplateView, UpdateView
from hellosign import jobs
from hellosign.models import StudentConsentTemplate
from profiles.decorators import not_for_role, only_for_role, UserRole
from profiles.views import EditProfileMixin
from .forms import *
from .models import StudentProfile

only_for_student = only_for_role(UserRole.student)
unapproved_ok = whitelist('unapproved_students')

def banner_membership_blacklisted(request):
    membership_set = request.user.membership_set.filter(is_active=True)
    return any(membership.id in settings.AI_BANNER_STUDENT_BLACKLIST for membership in membership_set)


class CreateView(EditProfileMixin, CreateView):
    model = StudentProfile
    form_class = NewStudentProfileForm

    def get_success_url(self):
        return reverse("students:unapproved")

create = not_for_role(UserRole.student, redirect="students:edit_profile")(CreateView.as_view())

class EditView(EditProfileMixin, UpdateView):
    model = StudentProfile
    form_class = StudentProfileEditForm

    def get_success_url(self):
        messages.success(self.request, "Your changes were saved.")
        return reverse("students:edit_profile")

    def get_object(self, queryset=None):
        return self.request.user.studentprofile

edit = only_for_student(EditView.as_view())

class EditEmailView(EditProfileMixin, UpdateView):
    model = StudentProfile
    form_class = StudentEmailForm

    def form_valid(self, form):
        self.object = form.save()

        consent = StudentConsentTemplate()
        signature = consent.signature(self.object.user)
        if not signature.signed:
            jobs.update_email(signature.id)

        messages.success(self.request, "Your parent or guardian's email address has been updated.")
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', reverse("families:home")))

    def form_invalid(self, form):
        messages.error(self.request, form['email'].errors)
        return HttpResponseRedirect(self.request.META.get('HTTP_REFERER', reverse("families:home")))

    def get_object(self, queryset=None):
        return self.request.user.studentprofile

edit_email = unapproved_ok(only_for_student(EditEmailView.as_view()))

class HomeView(RedirectView):

    def get_redirect_url(self):
        memberships = self.request.user.membership_set.filter(is_active=True).order_by('display_name')
        if memberships:
            return reverse("students:membership", kwargs={"membership_id": memberships.first().id})
        return reverse("students:my_challenges")

home = only_for_student(HomeView.as_view())

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
        presenter = LearningSet([p.challenge for p in progresses], progresses)
        context['object_list'] = context['challenges'] = presenter.objects
        return context

my_challenges = only_for_student(ChallengesView.as_view())

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
        presenter = LearningSet(challenges, progresses)

        context['membership'] = membership
        context['challenges'] = presenter.objects
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
        presenter = LearningSet(challenges, progresses)
        context['challenges'] = context['object_list'] = presenter.objects
        return context

favorites = only_for_student(FavoritesView.as_view())

class UnapprovedView(TemplateView):
    template_name = "students/unapproved.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            email_form=StudentEmailForm(request=self.request, user=self.request.user),
            **kwargs
        )

unapproved = unapproved_only(UnapprovedView.as_view())

class ActivityView(DashboardMixin, ListView):
    template_name = "students/dashboard/activity.html"
    paginate_by = settings.DEFAULT_PER_PAGE
    context_object_name = 'activity'

    def get_queryset(self):
        return self.request.user.notifications.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        by_day = {}
        for notification in context['activity']:
            day = notification.timestamp.date()
            by_day[day] = by_day.get(day, [])
            by_day[day].append(notification)

        context.update({
            "activity_by_day": by_day,
        })

        return context

activity = only_for_student(ActivityView.as_view())
