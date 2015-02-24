from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from videos.models import Video
from images.models import Image
from enum import Enum
from django.utils.safestring import mark_safe
from django.db.models.signals import post_save
from cmemails import deliver_email
from django.db import connection
from .validators import validate_color


class Stage(Enum): # this is used in challenge views and challenge and comment models
    inspiration = 0
    plan = 1
    build = 2
    test = 3
    reflect = 4

class Theme(models.Model):
    name = models.TextField()
    icon = models.TextField(max_length=64, default="icon-neuroscience", help_text=mark_safe("This determines the icon that displays on the theme. Choose and icon by entering one of the following icon classes:<br><strong>icon-satellite icon-robotics icon-ocean icon-neuroscience icon-inventor icon-food icon-engineer icon-electrical icon-civil icon-builder icon-biomimicry icon-biomechanics icon-art icon-aerospace icon-compsci</strong><br /><br />Additionally available are the set of icons located here: <a href='http://getbootstrap.com/components/'>Bootstrap Glyphicons</a>. Enter both class names separated with a space. for example \"glyphicon glyphicon-film\" without quotes."))
    color = models.TextField(max_length=64, default="#84af49", help_text=mark_safe("Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>"))

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "Theme: name={}".format(self.name)

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:297] + "..." if len(self.text) > 300 else self.text
        
class Challenge(models.Model):
    name = models.TextField()
    description = models.TextField(help_text="One line of plain text, shown on the inspiration page")
    how_to_make_it = models.TextField(help_text="HTML, shown in the guide")
    learn_more = models.TextField(help_text="HTML, shown in the guide")
    mentor_guide = models.TextField(help_text="HTML, shown in the mentor guide", null=True, blank=True)
    materials_list = models.TextField(help_text="HTML")
    students = models.ManyToManyField(User, through='Progress', through_fields=('challenge', 'student'), null=True, related_name="challenges")
    theme = models.ForeignKey(Theme, null=True, blank=True, on_delete=models.SET_NULL)
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    plan_call_to_action = models.TextField(help_text="HTML, shown in the left column of the plan stage")
    build_call_to_action = models.TextField(help_text="HTML, shown in the left column of the build stage")
    plan_subheader = models.TextField(help_text="One line of plain text, shown below the plan stage header")
    build_subheader = models.TextField(help_text="One line of plain text, shown below the build stage header")
    reflect_subheader = models.TextField(help_text="One line of plain text, shown below the reflect stage header")
    reflect_questions = models.ManyToManyField(Question, null=True)
    favorited = models.ManyToManyField(User, through='Favorite', through_fields=('challenge', 'student'), null=True, related_name="favorite_challenges")
    draft = models.BooleanField(default=True, null=False, help_text="Drafts are not shown in the main challenge list")
    
    def get_absolute_url(self):
        return reverse('challenges:challenge', kwargs={
            'challenge_id': self.id,
        })

    def is_favorite(self, student):
        return Favorite.objects.filter(challenge=self, student=student).exists()

    def __str__(self):
        return "Challenge: id={}, name={}".format(self.id, self.name)

class Progress(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(User, related_name='progresses')
    started = models.DateTimeField(default=now)
    mentor = models.ForeignKey(User, related_name='mentored_progresses', null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.DateTimeField(null=True, blank=True)
    _materials_list = models.TextField(help_text="HTML", blank=True, db_column="materials_list")

    class Meta:
        verbose_name_plural = "progresses"

    @classmethod
    def unclaimed(cls, started_date=None):
        date_clause = ""
        if started_date:
            started_date = "%d-%d-%d" % (started_date.year, started_date.month, started_date.day)
            date_clause = "and DATE(challenges_progress.started) = DATE('%s')" % started_date
        query = """
        select distinct challenges_progress.* from challenges_progress 
        left join cmcomments_comment on challenges_progress.id = cmcomments_comment.challenge_progress_id 
        where cmcomments_comment.challenge_progress_id IS NOT NULL
        %s
        and challenges_progress.mentor_id IS NULL
        order by challenges_progress.started DESC
        """ % date_clause
        return cls.objects.raw(query)



    @classmethod
    def unclaimed_days(cls):
        query = """
        select distinct DATE(challenges_progress.started) as started, count(distinct challenges_progress.id) as count from challenges_progress 
        left join cmcomments_comment on challenges_progress.id = cmcomments_comment.challenge_progress_id 
        where cmcomments_comment.challenge_progress_id IS NOT NULL
        and challenges_progress.mentor_id IS NULL
        group by DATE(challenges_progress.started)
        order by started
        """
        cursor = connection.cursor()
        cursor.execute(query)
        return cursor.fetchall()


    def is_first_project(self):
        return self.student.progresses.count() == 1

    def approve(self):
        self.approved=now()
        self.save()
        if self.student.profile.birthday:
            deliver_email('project_completion', self.student.profile, progress=self, stage=Stage.reflect.name)


    def save(self, *args, **kwargs):
        if Progress.objects.filter(challenge=self.challenge, student=self.student).exclude(id=self.id).exists():
            raise ValidationError("There is already progress by this student on this challenge")
        if self.student.profile.is_mentor:
            raise ValidationError("Mentors can not start a challenge")
        if self.mentor and not self.mentor.profile.is_mentor:
            raise ValidationError("The mentor of a challenge must be a mentor")
        else:
            super(Progress, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('challenges:challenge_progress', kwargs={'challenge_id': self.challenge_id, 'username': self.student.username,})

    def get_unread_comments_for_user(self, user):
        if user == self.mentor:
            return self.comments.filter(read=False, user=self.student)
        elif user == self.student:
            return self.comments.filter(read=False, user=self.mentor)
        else:
            return self.comments.none()

    def get_student_images(self):
        return Image.objects.filter(comments__user=self.student, comments__challenge_progress=self)

    @property
    def materials_list(self):
        return self._materials_list if self._materials_list else self.challenge.materials_list

    @property
    def completed(self):
        # a progress is complete once a comment has been made on the Reflect stage
        return self.comments.filter(stage=Stage.reflect.value).exists()

    def student_username(self):
        return self.student.username

    def challenge_name(self):
        return self.challenge.name

    def mentor_username(self):
        return self.mentor.username if self.mentor else ''

    def __repr__(self):
        return "Progress: id={}, challenge_id={}, student_id={}".format(self.id, self.challenge_id, self.student_id)

    def __str__(self):
        return "Progress: id={}".format(self.id)

    def email_mentor_responded(self):
        if self.mentor:
            deliver_email('mentor_responded', self.student.profile, progress=self, mentor=self.mentor.profile)

    def email_student_responded(self):
        if self.mentor:
            deliver_email('student_responded', self.mentor.profile, progress=self, student=self.student.profile)

    def email_first_project(self):
        if self.is_first_project():
            deliver_email('first_project', self.student.profile)

def create_progress(sender, instance, created, **kwargs):
    if created and instance.is_first_project():
        instance.email_first_project()

post_save.connect(create_progress, sender=Progress)

class Favorite(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(User, related_name='favorites')

    class Meta:
        verbose_name_plural = "Favorites"

    def save(self, *args, **kwargs):
        if Favorite.objects.filter(challenge=self.challenge, student=self.student).exclude(id=self.id).exists():
            raise ValidationError("This challenge is already on your favorites")
        if self.student.profile.is_mentor:
            raise ValidationError("Mentors can not favorite a challenge")
        else:
            super(Favorite, self).save(*args, **kwargs)

class Example(models.Model): # media that a mentor has selected to be featured on the challenge inspiration page (can also be pre-populated by admins)
    challenge = models.ForeignKey(Challenge)
    progress = models.ForeignKey(Progress, null=True, blank=True, on_delete=models.SET_NULL, help_text="An optional association with a specific student's progress on a challenge.")
    _name = models.TextField(blank=True, verbose_name="name", db_column="name", help_text="The student's username in plain text. This can be left blank if a progress is set, in which case the progress's student username will be automatically used instead.")
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, help_text="An image to display in the gallery. If a video is also set, this will be the thumbnail. Each example must have an image or a video, or both, to be displayed correctly.")
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL, help_text="Each example must have an image or a video, or both, to be displayed correctly.")

    @property
    def name(self):
        if self._name: return self._name
        elif self.progress: return self.progress.student.username
        else: return ""

def create_example(sender, instance, created, **kwargs):
    if created:
        progress = instance.progress
        progress.student.profile.deliver_publish_email(progress)

post_save.connect(create_example, sender=Example)


class Filter(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False, help_text="name of the filter")
    color = models.CharField(max_length=7, blank=True, null=True, validators=[validate_color], help_text="Enter the background color in hex format. for example: #ffffff<br><br>Here are the brand colors for reference:<br> Blue: <strong>#44b1f5</strong> Green: <strong>#84af49</strong> Orange: <strong>#f16243</strong> Teal: <strong>#1bb2c4</strong> Yellow: <strong>#f1ac43</strong><br>gray-darker: <strong>#222222</strong> gray-dark: <Strong>#333333</strong> gray: <strong>#555555</strong> gray-light: <strong>#999999</strong> gray-lighter: <strong>#eee</strong>")
    challenges = models.ManyToManyField(Challenge, related_name='filters')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=False, null=False, db_index=True)

    
    def __str__(self):
        return "Filter: id={}, name={}".format(self.id, self.name)

    def __repr__(self):
        return "Filter: id={}, name={}".format(self.id, self.name)    

