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

class UserRole(Enum):
    none = 0
    student = 1
    mentor = 2
    educator = 3
    parent = 4

    @property
    def profile_class(self):
        if self.value == 0:
            return None
        return apps.get_model('%ss' % self.name, '%sProfile' % self.name.title())

    @property
    def profile_attr(self):
        if self.value == 0:
            return None
        return '%sprofile' % self.name

class BaseProfile(models.Model):
    class Meta:
        abstract = True

    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='%(class)s')

class NullProfile(object):

    def __getattr__(self, name):
        # "Called when an attribute lookup has not found the attribute in the usual places"
        # https://docs.python.org/3/reference/datamodel.html#object.__getattr__
        return None

class UserExtra(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='extra')
    role = models.SmallIntegerField(choices=[(role.value, role.name) for role in UserRole], default=UserRole.none.value)
    source = models.CharField(max_length=50, null=False, blank=True, default="")
    approved = models.BooleanField(default=False)
    last_active_on = models.DateTimeField(default=now)
    last_inactive_email_sent_on = models.DateTimeField(default=None, null=True, blank=True)
    first_login = models.BooleanField(default=True)

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

    def update_inactive_email_sent_on_and_save(self):
        self.last_inactive_email_sent_on = now()
        self.save(update_fields=['last_inactive_email_sent_on'])

class User(get_user_model()):
    class Meta:
        proxy = True

    @classmethod
    def cast(cls, user):
        user.__class__ = cls
        return user

    @property
    def profile(self):
        if hasattr(self, "studentprofile"):
            return self.studentprofile
        elif hasattr(self, "parentprofile"):
            return self.parentprofile
        elif hasattr(self, "mentorprofile"):
            return self.mentorprofile
        elif hasattr(self, "educatorprofile"):
            return self.educatorprofile
        return NullProfile()

# TODO: remove this model, when comfortable
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile')
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    city = models.TextField(blank=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
    title = models.TextField(blank=True, help_text="This is a mentor only field.")
    employer = models.TextField(blank=True, help_text="This is a mentor only field.")
    expertise = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_me = models.TextField(blank=True, help_text="This is a mentor only field.")
    organization = models.CharField(max_length=50, null=True, blank=True, help_text="This is an educator field.")
    about_me_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_me_image")
    about_me_video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_me_video")

    about_research = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_research_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_research_image")
    about_research_video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_research_video")

    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    child_profiles = models.ManyToManyField(
        "self",
        through="ParentConnection",
        through_fields=('parent_profile', 'child_profile'),
        related_name="parent_profiles",
        symmetrical=False,
    )

    @property
    def age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day)) #subtract a year if birthday hasn't occurred yet

    @property
    def should_add_email(self):
        return not self.user.email

    def is_underage(self):
        return self.age < 13
    is_underage.boolean = True

    def __str__(self):
        return "Profile: id={}, user_id={}".format(self.id, self.user_id)

    def is_parent_of(self, username, **kwargs):
        filters = {
            'parent_profile': self,
            'child_profile__user__username': username
        }
        for field in ['active', 'removed']:
            if field in kwargs:
                filters[field] = kwargs[field]
        return ParentConnection.objects.filter(**filters).exists()

class ParentConnection(models.Model):
    parent_profile = models.ForeignKey("Profile", related_name="connections_as_parent")
    child_profile = models.ForeignKey("Profile", related_name="connections_as_child")
    active = models.BooleanField(default=False)
    removed = models.BooleanField(default=False)
    retries = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "ParentConnection: {} -> {}, id={}".format(
            self.parent_profile.user.username,
            self.child_profile.user.username,
            self.id
        )

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
