from django.apps import apps
from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.utils.functional import cached_property
from images.models import Image
from videos.models import Video
from datetime import date, timedelta
from cmcomments.models import Comment
from django.utils.timezone import now
from enum import Enum
import importlib

def load_from_role_app(rolevalue, modulename, classname):
    role = UserRole(rolevalue)
    try:
        mod = importlib.import_module("%s.%s" % (role.app_name, modulename))
        cls = getattr(mod, classname)
        return cls
    except ModuleNotFoundError:
        return None

USER_ROLE_CONFIG = {
    'student': {
        'app': 'students',
        'profileclass': 'StudentProfile'
    },
    'mentor': {
        'app': 'mentors',
        'profileclass': 'MentorProfile'
    },
    'educator': {
        'app': 'educators',
        'profileclass': 'EducatorProfile'
    },
    'parent': {
        'app': 'parents',
        'profileclass': 'ParentProfile'
    },
    'family': {
        'app': 'families',
        'profileclass': 'FamilyProfile'
    }
}

class UserRole(Enum):
    none = 0
    student = 1
    mentor = 2
    educator = 3
    parent = 4
    family = 5

    @property
    def app_name(self):
        config = USER_ROLE_CONFIG.get(self.name, None)
        if not config:
            return None
        return config.get('app')

    @property
    def profile_class(self):
        config = USER_ROLE_CONFIG.get(self.name, None)
        if not config:
            return None
        return apps.get_model(self.app_name, config.get('profileclass'))

    @property
    def profile_attr(self):
        config = USER_ROLE_CONFIG.get(self.name, None)
        if not config:
            return None
        return config.get('profileclass').lower()

class BaseProfile(models.Model):
    class Meta:
        abstract = True

    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='%(class)s')

class NullProfile(object):

    def __getattr__(self, name):
        # "Called when an attribute lookup has not found the attribute in the usual places"
        # https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        return None

class UserExtraQuerySet(models.QuerySet):
    def role(self, role):
        if type(role) == int:
            role = UserRole(role)
        elif type(role) == str:
            role = UserRole[role.lower()]

        return self.filter(role=role.value)

    def inactive_since(self, days_ago):
        startdate = now()
        enddate = startdate - timedelta(days=days_ago)
        return self.filter(last_active_on__lt=enddate)

class UserExtra(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='extra')
    role = models.SmallIntegerField(choices=[(role.value, role.name) for role in UserRole], default=UserRole.none.value)
    source = models.CharField(max_length=50, null=False, blank=True, default="")
    last_active_on = models.DateTimeField(default=now)
    last_inactive_email_sent_on = models.DateTimeField(default=None, null=True, blank=True)
    first_login = models.BooleanField(default=True)

    objects = UserExtraQuerySet.as_manager()

    @property
    def profile(self):
        return User.profile_for(self.user)

    @classmethod
    def inactive_mentors(cls):
         startdate = now()
         enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
         return cls.objects.filter(last_active_on__lt=enddate, role=UserRole.mentor.value, last_inactive_email_sent_on=None)

    @classmethod
    def inactive_students(cls):
         startdate = now()
         enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
         return cls.objects.filter(last_active_on__lt=enddate,role=UserRole.student.value, last_inactive_email_sent_on=None)

    @cached_property
    def in_active_membership(self):
        return self.user.membership_set.filter(is_active=True).count() > 0

    @property
    def is_approved(self):
        """
        Commenting because the semantics here are weird.

        Replaces old `approved` flag; meant to provide some generalized notion of whether a user
        is approved/has full access/is in some way limited on the site without necessarily knowing
        what type of user they are.

        For now, assumes they are "approved" (whatever that means) unless the active profile has
        `full_access=False`.
        """
        profile = self.profile
        if hasattr(profile, "full_access"):
            return profile.full_access
        else:
            return True

    @property
    def role_name(self):
        return UserRole(self.role).name

    @property
    def is_student(self):
        return UserRole(self.role) == UserRole.student

    @property
    def is_mentor(self):
        return UserRole(self.role) == UserRole.mentor

    @property
    def is_educator(self):
        return UserRole(self.role) == UserRole.educator

    @property
    def is_parent(self):
        return UserRole(self.role) == UserRole.parent

    @property
    def is_family(self):
        return UserRole(self.role) == UserRole.family

    @property
    def should_add_email(self):
        return not self.user.email

    @property
    def user_type(self):
        if self.user.is_superuser:
            return 'admin'
        elif self.is_mentor:
            return 'mentor'
        elif self.is_student:
            if self.user.studentprofile.birthday and self.user.studentprofile.is_underage():
                return 'underage student'
            else:
                return 'student'
        elif self.is_educator:
            return 'educator'
        elif self.is_parent:
            return 'parent'

    @property
    def send_welcome(self):
        return UserRole(self.role) not in [UserRole.none, UserRole.mentor]

    @property
    def show_classroom_survey(self):
        return not (self.source and self.source in ['family_science'])

    def set_active(self):
        self.last_active_on = now()
        return self.save(update_fields=['last_active_on'])

    def check_for_profile(self):
        role = UserRole(self.role)
        if role.profile_attr and not hasattr(self.user, role.profile_attr):
            self.user.skip_welcome_email = True # can't check underage when profiles created this way
            role.profile_class.objects.create(user=self.user)

for role in UserRole:
    if role.app_name:
        setattr(UserExtra, role.app_name, UserExtra.objects.role(role))

class User(get_user_model()):
    class Meta:
        proxy = True

    @classmethod
    def cast(cls, user):
        user.__class__ = cls
        return user

    @classmethod
    def profile_for(cls, user):
        return cls.cast(user).profile

    @property
    def profile(self):
        role = UserRole(self.extra.role)
        if role.profile_attr:
            return getattr(self, role.profile_attr)
        return NullProfile()

class ImpactSurvey(models.Model):
    student_count = models.PositiveIntegerField(default=0, blank=True)
    teacher_count = models.PositiveIntegerField(default=0, blank=True)
    challenge_count = models.PositiveIntegerField(default=0, blank=True)
    in_classroom = models.BooleanField(default=False)
    out_of_classroom = models.BooleanField(default=False)
    hours_per_challenge = models.PositiveIntegerField(default=0, blank=True)
    comment = models.TextField(blank=True, default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "ImpactSurvey: id={}, user_id={}".format(self.id, self.user_id)
