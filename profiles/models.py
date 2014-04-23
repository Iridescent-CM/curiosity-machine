from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile')
    is_mentor = models.BooleanField(default=False)
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    city = models.TextField(blank=True)
    nickname = models.CharField(max_length=30, blank=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
    title = models.TextField(blank=True)

    def get_absolute_url(self):
        if self.is_mentor:
            return reverse('profiles:mentor_profile_details', kwargs={'username': self.user.username})
        else:
            return reverse('profiles:student_profile_details', kwargs={'username': self.user.username})

    @property
    def is_student(self):
        return not self.is_mentor

    def __str__(self):
        return "Profile: id={}, user={}".format(self.id, self.user.username)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
