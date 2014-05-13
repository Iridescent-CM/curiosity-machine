from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from images.models import Image

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name='profile')
    is_mentor = models.BooleanField(default=False)
    birthday = models.DateField(blank=True,null=True)
    gender = models.CharField(max_length=1,blank=True)
    city = models.TextField(blank=True)
    nickname = models.CharField(max_length=30, blank=True)
    parent_first_name = models.TextField(blank=True)
    parent_last_name = models.TextField(blank=True)
    title = models.TextField(blank=True, help_text="This is a mentor only field.")
    employer = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_me = models.TextField(blank=True, help_text="This is a mentor only field.")
    about_research = models.TextField(blank=True, help_text="This is a mentor only field.")
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)

    @property
    def is_student(self):
        return not self.is_mentor

    def __str__(self):
        return "Profile: id={}, user_id={}".format(self.id, self.user_id)

    def get_user_image_url(self):
        if self.image:
            return self.image.url
        else:
            return "http://placekitten.com/60/80" #TODO: Add a real placeholder instead of using placekittens

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
