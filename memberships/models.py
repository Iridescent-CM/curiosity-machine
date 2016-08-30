from os.path import splitext, basename
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.core.files import File
from django.conf import settings
from django.utils.timezone import now
from tempfile import TemporaryFile
from datetime import timedelta
from challenges.models import Challenge
from profiles.models import UserRole, Profile
from memberships.importer import BulkImporter, Status
from memberships.validators import member_import_csv_validator
import logging

logger = logging.getLogger(__name__)


class Membership(models.Model):
    name = models.CharField(unique=True, max_length=255, null=False, blank=False)
    display_name = models.CharField(
        max_length=26,
        null=False,
        help_text="The membership name users will see on the site (max 26 characters)."
    )
    expiration = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    challenges = models.ManyToManyField(Challenge, blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, through='Member', through_fields=('membership', 'user'), blank=True)

    @classmethod
    def filter_by_challenge_access(cls, user, challenge_ids):
        if not settings.FEATURE_FLAGS.get('enable_membership_access_controls', False):
            return challenge_ids

        if user.is_authenticated() and (user.is_staff or user.profile.is_mentor):
            return challenge_ids

        query = Q(id__in=challenge_ids, free=True)
        if user.is_authenticated():
            query = query | Q(id__in=challenge_ids, membership__members=user)

        return Challenge.objects.filter(query).values_list('id', flat=True)

    @classmethod
    def share_membership(cls, username1, username2):
        if not settings.FEATURE_FLAGS.get('enable_membership_access_controls', False):
            return False

        return Member.objects.filter(user__username=username1, membership__members__username=username2).exists()

    def limit_for(self, role):
        obj = self.memberlimit_set.filter(role=role).first()
        if obj:
            return obj.limit
        return None

    def __str__(self):
        return "id:%s, name:%s" % (self.id, self.name)

class Member(models.Model):
    class Meta:
        unique_together = ("membership", "user")

    membership = models.ForeignKey(Membership)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    def clean(self):
        role = self.user.profile.role
        limit = self.membership.limit_for(role)
        if limit != None:
            count = (self.membership.member_set
                .exclude(id=self.id)
                .filter(user__profile__role=role)).count()
            if count >= limit:
                raise ValidationError("%s membership in %s limited to %d" % (UserRole(role).name, self.membership, limit))

class MemberLimit(models.Model):
    class Meta:
        unique_together = ("role", "membership")
    role = models.SmallIntegerField(choices=[(role.value, role.name) for role in UserRole], default=UserRole.none.value)
    limit = models.PositiveIntegerField(null=False, blank=True, default=0)
    membership = models.ForeignKey(Membership, null=False, on_delete=models.CASCADE)

    @property
    def current(self):
        return self.membership.member_set.filter(user__profile__role=self.role).count()

def member_import_path(instance, filename):
    return "memberships/%d/import/%s" % (instance.membership.id, filename)

class StaleManager(models.Manager):
    def __init__(self, settings_key, *args, **kwargs):
        self.default_days = int(getattr(settings, settings_key))
        return super().__init__(*args, **kwargs)

    def get_queryset(self):
        return self.older_than(self.default_days)

    def older_than(self, days=None):
        qs =  super().get_queryset()
        if days != None:
            qs = qs.filter(updated_at__lt=self.threshold(days))
        return qs

    def threshold(self, days=None):
        days = days if days != None else self.default_days
        return now() - timedelta(days=days)

class MemberImport(models.Model):
    input = models.FileField(upload_to=member_import_path, validators=[member_import_csv_validator], help_text="Input file must be csv format, utf-8 encoding")
    output = models.FileField(null=True, blank=True, upload_to=member_import_path)
    membership = models.ForeignKey(Membership, null=False, on_delete=models.CASCADE)
    status = models.SmallIntegerField(null=True, blank=True, choices=[(status.value, status.name) for status in Status])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    stale_objects = StaleManager("MEMBER_IMPORT_EXPIRATION_DAYS")

    @staticmethod
    def output_name(name):
        return "%s_result%s" % splitext(name)

    def process(self):
        """
        This method calls BulkImporter to do the heavy lifting (in a more easily testable way)
        and maps the results back to the MemberImport object for persistence
        """
        try:
            from memberships.forms import RowImportForm
            importer = BulkImporter(RowImportForm, membership=self.membership)
            with TemporaryFile(mode="w+t") as fp:
                result = importer.call(self.input, fp)
                self.status = result["final"].value
                self.output.save(self.output_name(basename(self.input.name)), File(fp), save=False)
                self.save()
        except Exception as ex:
            logger.warning("Unexpected exception processing member import file %s" % self.input.name, exc_info=ex)
            self.status = Status.exception.value
            self.save(update_fields=['status'])

import django_rq
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver

@receiver(pre_save, sender=Member)
def clean_first(sender, instance, **kwargs):
    instance.full_clean()

@receiver(post_save, sender=MemberImport)
def process(sender, instance, created, **kwargs):
    if created:
        django_rq.enqueue(instance.process)

@receiver(post_delete, sender=MemberImport)
def delete_files(sender, instance, **kwargs):
    if instance.input.name:
        instance.input.delete(save=False)
    if instance.output.name:
        instance.output.delete(save=False)
