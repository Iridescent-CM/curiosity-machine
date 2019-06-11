from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models, connection
from django.db.models import Q
from django.utils.safestring import mark_safe
from django.utils.timezone import now
from django_s3_storage.storage import S3Storage
from curiositymachine import signals
from images.models import Image
from videos.models import Video
from enum import Enum
from functools import reduce
from feedback.models import FeedbackQuestion


class Stage(Enum): # this is used in challenge views and challenge and comment models
    inspiration = 0
    plan = 1
    build = 2
    test = 3
    reflect = 4

class Theme(models.Model):
    name = models.TextField()
    icon = models.TextField(max_length=64, default="icon-neuroscience", help_text=mark_safe("This determines the icon that displays on the theme. Choose and icon by entering one of the following icon classes:<br><strong>icon-satellite icon-robotics icon-ocean icon-neuroscience icon-inventor icon-food icon-engineer icon-electrical icon-civil icon-builder icon-biomimicry icon-biomechanics icon-art icon-aerospace icon-compsci icon-materials</strong><br /><br />Additionally available are the set of icons located here: <a href='http://getbootstrap.com/components/'>Bootstrap Glyphicons</a>. Enter both class names separated with a space. for example \"glyphicon glyphicon-film\" without quotes."))

    class Meta:
        ordering = ['name']

    def __str__(self):
        return "Theme: name={}".format(self.name)

class Question(models.Model):
    text = models.TextField()

    def __str__(self):
        return self.text[:297] + "..." if len(self.text) > 300 else self.text

class Challenge(models.Model):

    DIFFICULTY_LEVELS = ((1, 1), (2, 2), (3, 3))

    class Meta:
        ordering = ["order", "-id"]

    name = models.TextField()
    description = models.TextField(help_text="One line of plain text, shown on the inspiration page")
    how_to_make_it = models.TextField(help_text="HTML, shown in the guide")
    learn_more = models.TextField(help_text="HTML, shown in the guide")
    materials_list = models.TextField(help_text="HTML")
    doers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Progress',
        through_fields=('challenge', 'owner'),
        related_name="challenges"
    )
    themes = models.ManyToManyField(Theme, blank=True, related_name='challenges')
    video = models.ForeignKey(Video, null=True, blank=True, on_delete=models.SET_NULL)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL)
    landing_image = models.ForeignKey(Image, null=True, blank=True, related_name="+", on_delete=models.PROTECT, help_text="Image size should be a 4:3 ratio, at least 720px wide for best results. Jpg, png, or gif accepted.")
    build_call_to_action = models.TextField(help_text="HTML, shown in the left column of the build stage")
    reflect_questions = models.ManyToManyField(Question)
    favorited = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Favorite', through_fields=('challenge', 'student'), related_name="favorite_challenges")
    draft = models.BooleanField(default=True, null=False, help_text="Drafts are not shown in the main challenge list")
    free = models.BooleanField(default=True, null=False, help_text="Free challenges are available to users regardless of membership")
    difficulty_level = models.PositiveSmallIntegerField(
        choices=DIFFICULTY_LEVELS,
        default=1,
        help_text="From 1 (easy) to 3 (difficult)"
    )

    order = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Challenges will be shown in ascending numeric order, with blanks last",
        verbose_name="Order preference"
    )
    feedback_question = models.ForeignKey(FeedbackQuestion, null=True, blank=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse('challenges:preview_inspiration', kwargs={
            'challenge_id': self.id,
        })

    def is_favorite(self, student):
        return Favorite.objects.filter(challenge=self, student=student).exists()

    def __str__(self):
        return "Challenge: id={}, name={}".format(self.id, self.name)

class Progress(models.Model):
    challenge = models.ForeignKey(Challenge)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='progresses')
    started = models.DateTimeField(default=now)
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='mentored_progresses', null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.DateTimeField(null=True, blank=True)
    _materials_list = models.TextField(help_text="HTML", blank=True, db_column="materials_list")

    class Meta:
        verbose_name_plural = "progresses"
        unique_together = ('challenge', 'owner',)

    def is_first_project(self):
        return self.owner.progresses.count() == 1

    def save(self, *args, **kwargs):
        if Progress.objects.filter(challenge=self.challenge, owner=self.owner).exclude(id=self.id).exists():
            raise ValidationError("There is already progress by this user on this challenge")
        else:
            super(Progress, self).save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('challenges:challenge_progress', kwargs={'challenge_id': self.challenge_id, 'username': self.owner.username,})

    def get_unread_comments_for_user(self, user):
        return user.notifications.filter(target_object_id=self.id, target_content_type=ContentType.objects.get_for_model(self)).unread()

    def get_owner_images(self):
        return Image.objects.filter(comments__user=self.owner, comments__challenge_progress=self)

    @property
    def materials_list(self):
        return self._materials_list if self._materials_list else self.challenge.materials_list

    @property
    def completed(self):
        return self.comments.filter(stage=Stage.reflect.value, user_id=self.owner_id).exists()

    @property
    def most_recent(self):
        return self.comments.order_by('-created').first()

    @property
    def object_id(self):
        return self.challenge_id

    def owner_username(self):
        return self.owner.username

    def challenge_name(self):
        return self.challenge.name

    def mentor_username(self):
        return self.mentor.username if self.mentor else ''

    def __repr__(self):
        return "Progress: id={}, challenge_id={}, owner_id={}".format(self.id, self.challenge_id, self.owner_id)

    def __str__(self):
        return "Progress: id={}".format(self.id)

class Favorite(models.Model):
    challenge = models.ForeignKey(Challenge)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='favorites')

    class Meta:
        verbose_name_plural = "Favorites"

    def save(self, *args, **kwargs):
        if Favorite.objects.filter(challenge=self.challenge, student=self.student).exclude(id=self.id).exists():
            raise ValidationError("This challenge is already on your favorites")
        else:
            super(Favorite, self).save(*args, **kwargs)

class ExampleQuerySet(models.QuerySet):

    def for_gallery(self, **kwargs):
        challenge_id = kwargs.get('challenge_id', None) or kwargs.get('challenge').id
        user = kwargs.get('user', None)
        f = Q(approved=True)
        if user:
            f = f | Q(progress__owner=user, approved=None)
        return self.filter(progress__challenge_id=challenge_id).filter(f).order_by('-id')

    def for_gallery_preview(self, **kwargs):
        return self.for_gallery(**kwargs)[:4]

    def from_progress(self, **kwargs):
        progress = kwargs.get('progress')
        return self.filter(progress=progress)

    def status(self, **kwargs):
        qs = []
        if 'approved' in kwargs:
            if kwargs.get('approved'):
                qs.append(Q(approved=True))
            else:
                qs.append(~Q(approved=True))
        if 'pending' in kwargs:
            if kwargs.get('pending'):
                qs.append(Q(approved__isnull=True))
            else:
                qs.append(Q(approved__isnull=False))
        if 'rejected' in kwargs:
            if kwargs.get('rejected'):
                qs.append(Q(approved=False))
            else:
                qs.append(~Q(approved=False))

        if len(qs) > 0:
            return self.filter(reduce(lambda a, b: a | b, qs))
        else:
            return self

    def reject(self, user=None):
        return self.update(approved=False)
    reject.queryset_only = True

    def approve(self, user=None):
        return self.update(approved=True)
    approve.queryset_only = True

class Example(models.Model): # media that a mentor has selected to be featured on the challenge inspiration page (can also be pre-populated by admins)
    progress = models.ForeignKey(Progress, null=False, blank=False, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, null=True, blank=True, on_delete=models.SET_NULL, help_text="An image to display in the gallery. If a video is also set, this will be the thumbnail. Each example must have an image or a video, or both, to be displayed correctly.")
    approved = models.NullBooleanField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ExampleQuerySet().as_manager()

    @property
    def name(self):
        if self.progress: return self.progress.owner.username
        else: return ""

    @property
    def challenge(self):
        return self.progress.challenge

    def __str__(self):
        return "Example: id={}".format(self.id)

class Filter(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False, help_text="name of the filter")
    challenges = models.ManyToManyField(Challenge, related_name='filters')
    header_template = models.CharField(max_length=128, blank=True, null=True, help_text="Path to template containing header to display on filtered view")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    visible = models.BooleanField(default=False, null=False, db_index=True)


    def __str__(self):
        return "Filter: id={}, name={}".format(self.id, self.name)

    def __repr__(self):
        return "Filter: id={}, name={}".format(self.id, self.name)

class Resource(models.Model):
    name = models.CharField(
        max_length=128,
        help_text='Title for the resource, e.g. “Grade 3-5 Mini Unit”.',
    )
    description = models.TextField(
        help_text="Text that describes the resource. Should be < 50 words.",
    )
    challenge = models.ForeignKey(
        Challenge,
        null=True,
        help_text="The challenge that this resource should be associated with.",
    )

    def __str__(self):
        return "Resource: id={}, name={}".format(self.id, self.name)

resource_storage = S3Storage(aws_s3_metadata={
    "Content-Disposition": "attachment"
})

class ResourceFile(models.Model):
    file = models.FileField(upload_to="challenge_resource/%Y/%m/%d/", storage=resource_storage)
    link_text = models.CharField(
        max_length=64,
        null=True,
        help_text="Text that goes on a button. Keep it short (1 - 3 words).",
    )
    resource = models.ForeignKey(Resource)
