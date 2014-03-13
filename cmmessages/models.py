from django.db import models
from django.conf import settings 
from challenges.models import Challenge
from cmauth.user_role import Role
# from lck.django.common.models import TimeTrackable

class Conversation(models.Model): # there is only one of these for each pair of users who message one another
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="conversations_as_mentor")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="conversations_as_student")
    challenge = models.ForeignKey(Challenge, related_name="conversation")
    
    def save(self, *args, **kwargs):
        if Conversation.objects.filter(mentor=self.mentor, student=self.student, challenge=self.challenge).exists():
            raise ValidationError("there must not already be a conversation with these two users for this challenge")
        else:
            super(Conversation, self).save(*args, **kwargs)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, related_name="messages", blank=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages_sent")
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="messages_received")
    challenge = models.ForeignKey(Challenge, related_name="messages")
    text = models.TextField()
    read = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        '''sets self.conversation and then saves -- self.conversation is always automatically set
           and any manually defined value is discarded in this step. also sets self.conversation to unread for recipient'''
        if not self.id: # if this is a new save, NOT just marking as archived/etc
            if self.sender.role == Role.STUDENT:
                try:                
                    c = Conversation.objects.get(mentor=self.recipient, student=self.sender, challenge=self.challenge)
                except Conversation.DoesNotExist:
                    c = Conversation(mentor=self.recipient, student=self.sender)
                    c.save()
            elif self.sender.role == Role.MENTOR:
                try:
                    c = Conversation.objects.get(mentor=self.sender, student=self.recipient, challenge=self.challenge)
                except Conversation.DoesNotExist:
                    c = Conversation(mentor=self.sender, student=self.recipient)
                    c.save()
            self.conversation = c
        super(Message, self).save(*args, **kwargs)


    # class Meta:
    #     ordering = ('-created',)

