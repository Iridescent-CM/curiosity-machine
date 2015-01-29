from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from images.models import Image
from videos.models import Video
from datetime import date, timedelta
from cmcomments.models import Comment
from cmemails import deliver_email
from django.utils.timezone import now

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile')
    is_student = models.BooleanField(default=False, verbose_name="Student access")
    is_mentor = models.BooleanField(default=False, verbose_name="Mentor access")
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
