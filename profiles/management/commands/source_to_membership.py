from django.core.management.base import BaseCommand, CommandError
from memberships.models import Membership, Member
from profiles.models import Profile
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Add accounts with source to membership'

    def add_arguments(self, parser):
        parser.add_argument(
            "source",
            action="store",
            help="source value to match"
        )
        parser.add_argument(
            "membership_id",
            action="store",
            type=int,
            help="id of membership"
        )

    def handle(self, *args, **options):
        membership = Membership.objects.get(pk=options['membership_id'])
        profiles = Profile.objects.filter(source=options['source']).exclude(user__membership=membership)
        for profile in profiles:
            user = profile.user
            Member.objects.create(membership=membership, user=user)
            logger.info("Added %s to %s" % (user, membership))
