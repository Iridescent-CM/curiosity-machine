from django.db import models
from challenges.models import Challenge
from profiles.models import UserRole
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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

from django_s3_storage.storage import S3Storage
from django.core.exceptions import ValidationError
from django.template.defaultfilters import filesizeformat
from django.conf import settings
import csv

def member_import_csv_validator(csv_file):
    """
    Validates that CSVs used for member import are small enough to keep
    in memory, and readable as CSVs. Does not validate that members can
    necessarily be created from the data within.
    """

    if csv_file.size > settings.FILE_UPLOAD_MAX_MEMORY_SIZE:
        raise ValidationError("File is too large (%s)" % filesizeformat(csv_file.size))
    contents = csv_file.read()
    csv_file.seek(0)
    try:
        contents = contents.decode('utf-8')
    except UnicodeDecodeError:
        raise ValidationError("File does not appear to be UTF-8 encoded")
    except:
        raise ValidationError("Unknown error while decoding file")

    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(contents)
    except csv.Error:
        raise ValidationError("Not a valid CSV file")

class MemberImport(models.Model):
    input = models.FileField(upload_to="memberships/imports/", storage=S3Storage(), validators=[member_import_csv_validator])
    membership = models.ForeignKey(Membership, null=False, on_delete=models.CASCADE)

from django.db.models.signals import pre_save
from django.dispatch import receiver
@receiver(pre_save, sender=Member)
def clean_first(sender, instance, **kwargs):
    instance.full_clean()
