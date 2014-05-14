from django.db import models
from django.contrib.auth.models import User

class Module(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=70)
    text = models.TextField()

    class Meta:
        ordering = ('id',)

    def __str__(self):
        return "Module {}: {}".format(self.id, self.title)

class Comment(models.Model):
    module = models.ForeignKey(Module, related_name='comments')
    thread = models.ForeignKey(Comment, related_name='replies', null=True, blank=True) # if this is null, the comment is the start of a new thread; otherwise this foreign key must point to another comment that is the start of a new thread
    user = models.ForeignKey(User, related_name='mentor_training_comments')
    text = models.TextField()
    created = models.DateTimeField(default=now)

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return "Comment: id={id}, user_id={user_id}, module_id={module_id}, text={text}".format(id=self.id, user_id=self.user_id, module_id=self.module_id text=self.text[:45] + "..." if len(self.text) > 50 else self.text)
