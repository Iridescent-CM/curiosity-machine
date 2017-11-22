from django.core.management.base import BaseCommand, CommandError
from memberships.models import Membership, Member
from profiles.models import UserExtra
import logging

logger = logging.getLogger(__name__)

def add_all(source, membership_id):
    membership = Membership.objects.get(pk=membership_id)
    userextras = UserExtra.objects.filter(source=source).exclude(user__membership=membership)
    for userextra in userextras:
        user = userextra.user
        Member.objects.create(membership=membership, user=user)
        logger.info("Added %s to %s" % (user, membership))

class Command(BaseCommand):
    help = 'Add accounts with sources to memberships'

    def add_arguments(self, parser):
        parser.add_argument(
            "specifiers",
            action="store",
            nargs="+",
            help="source:membership_id pairs"
        )

    def handle(self, *args, **options):
        for specifier in options['specifiers']:
            try:
                (source, membership_id) = specifier.split(':')
                add_all(source, membership_id)
            except ValueError:
                raise CommandError(
                    ("Unable to parse specifier %s. Specifiers should be " +
                    "the source and membership id joined by a colon.") % specifier
                )
