from django.db import models
from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from images.models import Image
from videos.models import Video
from datetime import date, timedelta
from cmcomments.models import Comment
from cmemails import deliver_email
from django.utils.timezone import now
from uuid import uuid4
import time

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile')
    is_student = models.BooleanField(default=False, verbose_name="Student access")
    is_mentor = models.BooleanField(default=False, verbose_name="Mentor access")
    is_educator = models.BooleanField(default=False, verbose_name="Educator access")
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    city = models.TextField(blank=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)

    title = models.TextField(blank=True, help_text="This is a mentor only field.")
    employer = models.TextField(blank=True, help_text="This is a mentor only field.")
    expertise = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_me = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_me_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_me_image")
    about_me_video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_me_video")

    about_research = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_research_image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_research_image")
    about_research_video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="about_research_video")

    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.BooleanField(default=False)
    last_active_on = models.DateTimeField(default=now)
    #this field will be cleared once the user becomes active
    last_inactive_email_sent_on = models.DateTimeField(default=None, null=True, blank=True)
    shown_intro = models.BooleanField(default=False)

    @classmethod
    def inactive_mentors(cls):
        startdate = now()
        enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_MENTOR))
        return cls.objects.filter(last_active_on__lt=enddate, is_mentor=True, last_inactive_email_sent_on=None)

    @classmethod
    def inactive_students(cls):
        startdate = now()
        enddate = startdate - timedelta(days=int(settings.EMAIL_INACTIVE_DAYS_STUDENT))
        return cls.objects.filter(last_active_on__lt=enddate,is_student=True, last_inactive_email_sent_on=None)

    @classmethod
    def consent_student(cls, token, signature):
        invitation = ConsentInvitation.objects.get(code=token)
        profile = invitation.user.profile
        UnderageConsent.objects.create(signature=signature, profile=profile)
        profile.approved = True
        profile.save(update_fields=['approved'])
        deliver_email('activation_confirmation', profile, digitally_signed=True)
        invitation.delete()
        return profile

    @property
    def age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day)) #subtract a year if birthday hasn't occurred yet

    @property
    def user_type(self):
        if self.user.is_superuser:
            return 'admin'
        elif self.is_mentor:
            return 'mentor'
        elif self.birthday and self.is_underage:
            return 'underage student'
        else:
            return 'student'

    def is_underage(self):
        return self.age <= 13

    def set_active(self):
        self.last_active_on = now()
        return self.save(update_fields=['last_active_on'])

    def update_inactive_email_sent_on_and_save(self):
        self.last_inactive_email_sent_on = now()
        self.save(update_fields=['last_inactive_email_sent_on'])

    def __str__(self):
        return "Profile: id={}, user_id={}".format(self.id, self.user_id)

    # marks as approved and saves immediately, updating only the approved field
    def approve_and_save(self):
        self.approved = True
        self.save(update_fields=['approved'])

    def get_unread_comment_count(self):
        if self.is_mentor:
            return Comment.objects.exclude(user=self.user).filter(challenge_progress__mentor=self.user, read=False).count()
        else:
            return Comment.objects.exclude(user=self.user).filter(challenge_progress__student=self.user, read=False).count()

    def intro_video_was_played(self):
        self.shown_intro = True
        self.save(update_fields=['shown_intro'])

    def deliver_welcome_email(self):
        if self.is_mentor:
            deliver_email('welcome', self, cc=settings.MENTOR_RELATIONSHIP_MANAGERS)
        elif self.is_student and self.is_underage:
            if not ConsentInvitation.objects.filter(user=self.user).exists():
                invitation = ConsentInvitation.objects.create(user=self.user)
            else:
                invitation = self.user.consent_invitation
            invitation.send_welcome_invitation()
        else:
            deliver_email('welcome', self)

    def deliver_inactive_email(self):
        if self.birthday:
            deliver_email('inactive', self)

    def deliver_encouragement_email(self):
        deliver_email('encouragement', self)

    def deliver_publish_email(self, progress):
        deliver_email('publish', self, progress=progress)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class UnderageConsent(models.Model):
    profile = models.OneToOneField(Profile, null=False, blank=False, related_name="consent")
    signature = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Consent: id={}, profile={}".format(self.id, self.profile_id)
    def __repr__(self):
        return "Consent: id={}, profile={}".format(self.id, self.profile_id)

    def username(self):
        return self.profile.user.username

#just a description of an invitation, used in a welcome email for underage students
class ConsentInvitation(models.Model):
    user = models.OneToOneField(User, related_name="consent_invitation")
    code = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Code={} User={}".format(self.code, self.user)

    def __repr__(self):
        return "Code={} User={}".format(self.code, self.user)

    def send_welcome_invitation(self):
        deliver_email('welcome', self.user.profile, token=self.code)

def create_code(sender, instance, **kwargs):
    def unique_slug():
        string = uuid4()
        if ConsentInvitation.objects.filter(code=string).exists():
            return unique_slug()
        else:
            return string

    #check that this model hasn't been created yet
    if not instance.id:
        instance.code = unique_slug()

pre_save.connect(create_code, sender=ConsentInvitation)
