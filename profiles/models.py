from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from images.models import Image
from datetime import date, timedelta
from cmcomments.models import Comment
from cmemails import deliver_email
from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile')
    is_mentor = models.BooleanField(default=False)
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    city = models.TextField(blank=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
    title = models.TextField(blank=True, help_text="This is a mentor only field.")
    employer = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_me = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_research = models.TextField(blank=True, help_text="This is a mentor only field.")
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.BooleanField(default=False)
    last_active_on = models.DateTimeField(default=now)

    @classmethod
    def inactive_mentors(cls):
         startdate = now()
         enddate = startdate - timedelta(days=7)
         return cls.objects.filter(last_active_on__lt=enddate,is_mentor=True)

    @classmethod
    def inactive_students(cls):
         startdate = now()
         enddate = startdate - timedelta(days=14)
         return cls.objects.filter(last_active_on__lt=enddate,is_mentor=False)

    @property
    def is_student(self):
        return not self.is_mentor

    @property
    def age(self):
        today = date.today()
        return today.year - self.birthday.year - ((today.month, today.day) < (self.birthday.month, self.birthday.day)) #subtract a year if birthday hasn't occurred yet

    def is_underage(self):
        return self.age <= 13

    def update_last_active_on_and_save(self):
        self.last_active_on = now()
        return self.save(update_fields=['last_active_on'])

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

    def deliver_welcome_email(self):
        if self.is_mentor:
            deliver_email('welcome', self, cc=settings.MENTOR_RELATIONSHIP_MANAGERS)
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
