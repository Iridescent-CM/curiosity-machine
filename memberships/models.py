from challenges.models import Challenge
from curiositymachine.validators import validate_lowercase_slug
from datetime import timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from django.db import models
from django.db.models import Q
from django.utils.timezone import now, localtime
from memberships.importer import BulkImporter, Status
from memberships.validators import member_import_csv_validator
from os.path import splitext, basename
from profiles.models import UserRole
from tempfile import TemporaryFile
from units.models import Unit
import logging

logger = logging.getLogger(__name__)


class MembershipQuerySet(models.QuerySet):

    def expired(self, expiration=None, cutoff=None):
        if expiration is None:
            expiration = localtime(now()).date()
        if cutoff is None:
            return self.filter(expiration__lt=expiration)
        else:
            return self.filter(expiration__range=(cutoff, expiration - timedelta(days=1)))

    def expiring(self, expiration=None, cutoff=None):
        if expiration is None:
            expiration = localtime(now()).date()
        if cutoff is None:
            cutoff = expiration + timedelta(days=30)
        return self.filter(expiration__range=(expiration, cutoff))

class Membership(models.Model):
    name = models.CharField(
        unique=True,
        max_length=255,
        null=False,
        blank=False,
        help_text='Use this format: State-School Name-School Level-Grade Level e.g. “CA-Magnolia-ES-3”.',
    )
    display_name = models.CharField(
        max_length=26,
        null=False,
        help_text="The membership name users will see on the site (max 26 characters).",
    )
    slug = models.SlugField(
        unique=True,
        null=True,
        blank=True,
        validators=[validate_lowercase_slug],
        help_text="If provided, users can sign up for this membership at the slug url",
    )
    expiration = models.DateField(
        null=True,
        blank=True,
        help_text="Expired memberships will be automatically made inactive.",
    )
    is_active = models.BooleanField(
        "Active",
        null=False,
        default=True,
        help_text="Designates whether a membership is considered active. Unselect this when a membership expires instead of deleting it. To restore an inactive membership, enable this and update the expiration date."
    )
    notes = models.TextField(
        null=True,
        blank=True,
        help_text="Internal team notes that will not be displayed to users. Use this space to record information about a membership that doesn’t fit into other fields but is important for the team to know.",
    )
    hide_from_categories = models.BooleanField(
        default=False,
        help_text="Select this option if you don't want the membership to show up on the main challenges page for its members."
    )

    challenges = models.ManyToManyField(
        Challenge,
        blank=True,
        help_text="Users who are part of this membership will have access to the selected Challenges.",
    )
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Member',
        through_fields=('membership', 'user'),
        blank=True,
    )
    extra_units = models.ManyToManyField(
        Unit,
        blank=True,
        help_text="Users who are part of this membership will have access to these units in addition to the standard listed units."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MembershipQuerySet().as_manager()

    @classmethod
    def filter_by_challenge_access(cls, user, challenge_ids):
        if user.is_authenticated and user.is_staff:
            return challenge_ids

        query = Q(id__in=challenge_ids, free=True)
        if user.is_authenticated:
            query = query | Q(id__in=challenge_ids, membership__members=user, membership__is_active=True)

        return Challenge.objects.filter(query).values_list('id', flat=True)

    @classmethod
    def share_membership(cls, username1, username2):
        return Member.objects.filter(user__username=username1, membership__members__username=username2, membership__is_active=True).exists()

    def limit_for(self, role):
        obj = self.memberlimit_set.filter(role=role).first()
        if obj:
            return obj.limit
        return None

    def show_expiring_notice(self):
        today = localtime(now()).date()
        return (self.is_active 
            and self.expiration 
            and self.expiration >= today
            and (self.expiration - today) < timedelta(days=settings.MEMBERSHIP_EXPIRING_NOTICE_DAYS))

    @property
    def educators(self):
        return self.members.filter(extra__role=UserRole.educator.value)

    @property
    def students(self):
        return self.members.filter(extra__role=UserRole.student.value)

    @property
    def families(self):
        return self.members.filter(extra__role=UserRole.family.value)

    @property
    def listed_members(self):
        listed = [UserRole.family.value, UserRole.student.value, UserRole.educator.value]
        return self.members.filter(extra__role__in=listed)

    def __str__(self):
        return self.name

class Group(models.Model):
    class Meta:
        unique_together = ("membership", "name")

    membership = models.ForeignKey(Membership, null=False, blank=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, null=False, blank=False)
    members = models.ManyToManyField('Member', blank=True, through='GroupMember')

    def __str__(self):
        return "%s: %s" % (self.membership, self.name)

class GroupMember(models.Model):
    group = models.ForeignKey(Group, null=False, blank=False, on_delete=models.CASCADE)
    member = models.ForeignKey('Member', null=False, blank=False, on_delete=models.CASCADE)

    def clean(self):
        if self.member.membership != self.group.membership:
            raise ValidationError("Group and member must be part of the same membership")
        if not self.member.user.extra.is_student:
            raise ValidationError("Only students can be members of a group")

    def __str__(self):
        return "%s-%s: %s" % (self.group.membership, self.group.name, self.member.user)

class Member(models.Model):
    class Meta:
        unique_together = ("membership", "user")

    membership = models.ForeignKey(Membership, null=False, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=False, blank=False, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s: %s" % (self.membership, self.user)

    def clean(self):
        if not self.user_id or not self.membership_id:
            return
        role = self.user.extra.role
        limit = self.membership.limit_for(role)
        if limit != None:
            count = (self.membership.member_set
                .exclude(id=self.id)
                .filter(user__extra__role=role)).count()
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
        return self.membership.member_set.filter(user__extra__role=self.role).count()

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
        if days is None:
            days = self.default_days
        return qs.filter(updated_at__lt=self.threshold(days))

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

@receiver(pre_save, sender=GroupMember)
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
