from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse

class Module(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=70)
    text = models.TextField()
    mentors_done = models.ManyToManyField(User, null=True, related_name='completed_modules') # mentors listed here have completed the module

    class Meta:
        ordering = ('id',)

    def is_accessible_by_mentor(self, mentor):
        if mentor.profile.approved: # mentors who are approved can access any module, so that they can comment
            return True
        else:
            # they can only access if this is the next one by ID that they haven't finished, or lower (so, they can access older modules they have finished, and if they somehow skip one they can access that too)
            last_completed_module = mentor.completed_modules.order_by('id').last()
            if not last_completed_module:
                return self.id == Module.objects.order_by('id').first().id
            else:
                next_module = Module.objects.order_by('id').filter(id__gt=last_completed_module.id).first()
                if next_module:
                    return self.id <= next_module.id
                # else fall through and return None, but this shouldn't happen -- if there are no more modules to complete, then the mentor should already be approved

    def is_finished_by_mentor(self, mentor):
        return self.mentors_done.filter(id=mentor.id).exists()

    # add mentor to the done list, and also approve the mentor if this is the final module
    def mark_mentor_as_done(self, mentor):
        self.mentors_done.add(mentor)
        if self.id == Module.objects.order_by('id').last().id:
            mentor.profile.approve_and_save()
            return True

    def get_absolute_url(self):
        return reverse('training:module', args=[str(self.id)])

    def __str__(self):
        return "Module {}: {}".format(self.id, self.title)

class Comment(models.Model):
    module = models.ForeignKey(Module, related_name='comments')
    thread = models.ForeignKey("Comment", related_name='replies', null=True, blank=True) # if this is null, the comment is the start of a new thread; otherwise this foreign key must point to another comment that is the start of a new thread
    user = models.ForeignKey(User, related_name='mentor_training_comments')
    text = models.TextField()
    created = models.DateTimeField(default=now)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "Comment: id={id}, user_id={user_id}, module_id={module_id}, text={text}".format(id=self.id, user_id=self.user_id, module_id=self.module_id, text=self.text[:45] + "..." if len(self.text) > 50 else self.text)
