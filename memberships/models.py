from os.path import splitext, basename
from django.db import models
from django.contrib.auth.models import User
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


class Membership(models.Model):
    name = models.CharField(unique=True, max_length=255, null=False, blank=False)
    expiration = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    challenges = models.ManyToManyField(Challenge, blank=True)
    members = models.ManyToManyField(User, through='Member', through_fields=('membership', 'user'), blank=True)

    def limit_for(self, role):
        obj = self.memberlimit_set.filter(role=role).first()
        if obj:
            return obj.limit
        return None

    def __str__(self):
        return self.name

class Member(models.Model):
    class Meta:
        unique_together = ("membership", "user")

    membership = models.ForeignKey(Membership)
    user = models.ForeignKey(User)

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
        self.days_old = int(getattr(settings, settings_key))
        return super().__init__(*args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(updated_at__lt=self.threshold)

    @property
    def threshold(self):
        return now() - timedelta(days=self.days_old)

class MemberImport(models.Model):
    input = models.FileField(upload_to=member_import_path, validators=[member_import_csv_validator], help_text="Input file must be csv format, utf-8 encoding")
    output = models.FileField(null=True, blank=True, upload_to=member_import_path)
    membership = models.ForeignKey(Membership, null=False, on_delete=models.CASCADE)
    status = models.SmallIntegerField(null=True, choices=[(status.value, status.name) for status in Status])
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
        from memberships.forms import RowImportForm
        importer = BulkImporter(RowImportForm, membership=self.membership)
        with TemporaryFile(mode="w+t") as fp:
            result = importer.call(self.input, fp)
            self.status = result["final"].value
            self.output.save(self.output_name(basename(self.input.name)), File(fp), save=False)
            self.save()

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
