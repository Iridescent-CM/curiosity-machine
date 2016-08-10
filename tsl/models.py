from django.db.models.signals import pre_save
from django.db import models
from django.utils.timezone import now
from django.conf import settings
from videos.models import Video
from images.models import Image


class Question(models.Model):
	question_text = models.TextField(null=False, blank=False)

class Answer(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False)
    question = models.ForeignKey(Question)
    question_text = models.TextField(null=True, blank=False)
    answer_text = models.TextField(null=True, blank=True)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="answer")
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="answer")
    created = models.DateTimeField(default=now)
    
    class Meta:
    	unique_together = (("question", "user"),)

    @classmethod
    def get_or_build(cls, user, question_id):
    	answer = cls.objects.filter(user_id=user.id, question_id=question_id).first()
    	if not answer:
    		return cls(user=user,question_id=question_id)
    	else:
    		return answer

def cache_question_text(sender, instance, raw, using, update_fields, **kwargs):
    instance.question_text = Question.objects.get(id=instance.question_id).question_text


pre_save.connect(cache_question_text, sender=Answer)