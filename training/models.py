from django.db import models
from django.conf import settings
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from videos.models import Video
from images.models import Image
from curiositymachine import signals

class Module(models.Model):
    order = models.PositiveSmallIntegerField(unique=True, help_text="The order, starting from 1, in which this module will be displayed. The URL to the module page and all of the module's task pages are based on this number, so changing it will also change the URLs. This also affects trainee progression -- for instance, the first module is always available to trainees, and a trainee who completes all tasks in the lastly-ordered module is promoted to mentor ('approved'). The numbers should be sequential.")
    name = models.CharField(max_length=70)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="modules")
    draft = models.BooleanField(default=True, null=False, help_text="Drafts are not shown on the mentor home page")

    class Meta:
        ordering = ('order',)

    def is_accessible_by_mentor(self, mentor):
        return True
        # if mentor.profile.approved: # mentors who are approved can access any module, so that they can comment
        #     return True
        # elif mentor.is_staff: # staff members also get a free pass regardless of approval status
        #     return True
        # elif Module.objects.order_by('order').first() == self: # accessible if this is the first module (order_by is explicit here because the "previous module" check below could potentially crash if "class Meta" ordering unexpectedly changes)
        #     return True
        # elif self.is_finished_by_mentor(mentor): # accessible if this module is complete
        #     return True
        # elif Module.objects.filter(order__lt=self.order).order_by('order').last().is_finished_by_mentor(mentor): # accessible if the previous module in the ordering is complete
        #     return True
        # else:
        #     return False

    def is_finished_by_mentor(self, mentor):
        return not self.tasks.exclude(mentors_done=mentor).exists() # return True iff all of the tasks have been completed by the mentor

    def get_absolute_url(self):
        return reverse('training:module', args=[self.order])

    def __str__(self):
        return "Module {}: {}".format(self.order, self.name)

class Task(models.Model):
    module = models.ForeignKey(Module, related_name="tasks")
    order = models.PositiveSmallIntegerField(help_text="The order, starting from 1, in which this module will be displayed. The URL to the task page is based on this number, so changing it will also change the URL. The numbers must be unique within a single module. The numbers should also be sequential within a single module.")
    name = models.CharField(max_length=70)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="tasks")
    text = models.TextField(help_text="HTML")
    mentors_done = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='completed_tasks') # mentors listed here have completed the task
    completion_email_template = models.CharField(null=True, blank=True, max_length=70, help_text="Optional template name to send on task completion")

    class Meta:
        ordering = ('module', 'order',)
        unique_together= (['module', 'order'],)

    def is_finished_by_mentor(self, mentor):
        return self.mentors_done.filter(id=mentor.id).exists()

    def mark_mentor_as_done(self, mentor, approver):
        self.mentors_done.add(mentor)
        signals.approved_training_task.send(sender=approver, user=mentor, task=self)

    def get_absolute_url(self):
        return reverse('training:task', args=[self.module.order, self.order])

    def __str__(self):
        return "Task {} of module {}: {}".format(self.order, self.module.order, self.name)

class Comment(models.Model):
    task = models.ForeignKey(Task, related_name='comments')
    thread = models.ForeignKey("Comment", related_name='replies', null=True, blank=True) # if this is null, the comment is the start of a new thread; otherwise this foreign key must point to another comment that is the start of a new thread
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mentor_training_comments')
    text = models.TextField()
    created = models.DateTimeField(default=now)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, related_name="mentor_training_comments")
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, related_name="mentor_training_comments")

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return "Comment: id={id}, user_id={user_id}, task_id={task_id}, text={text}".format(id=self.id, user_id=self.user_id, task_id=self.task_id, text=self.text[:45] + "..." if len(self.text) > 50 else self.text)

    def replies_count(self):
        return self.replies.count()

    def recent_replies(self, limit=3):
        return self.replies.all().order_by('-created')[:limit][::-1]
