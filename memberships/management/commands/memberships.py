from argparse import ArgumentParser
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from memberships.models import *

class Command(BaseCommand):
    help = 'A memberships helper'

    def add_arguments(self, parser):
        self.parser = parser

        subparsers = parser.add_subparsers(
            title='subcommands',
            dest='subcommand',
            parser_class=ArgumentParser
        )

        add_members = subparsers.add_parser(
            'add_members',
            help="add users to memberships or groups",
            description="Add users listed in a file of usernames to a membership or group",
        )
        add_members.add_argument(
            "-f", "--filename",
            action="store",
            dest="filename",
            required=True,
            help="Name of file with list of usernames, one per line"
        )
        add_members.add_argument(
            "-m", "--membership",
            action="store",
            dest="membership_id",
            help="Id of membership to add users to"
        )
        add_members.add_argument(
            "-g", "--group",
            action="store",
            dest="group_id",
            help="Id of group to add users to"
        )

    def handle(self, *args, **options):
        sub = options.get('subcommand')
        if not sub:
            self.parser.print_help()
        elif hasattr(self, 'handle_%s' % sub):
            getattr(self, 'handle_%s' % sub)(**options)
        else:
            raise CommandError('Unknown subcommand: %s' % sub)

    def handle_add_members(self, **options):
        membership = None
        group = None

        if options.get('membership_id'):
            membership = Membership.objects.get(id=options.get('membership_id'))
        if options.get('group_id'):
            group = Group.objects.get(id=options.get('group_id'))

        if not (membership or group):
            raise CommandError('Specify -m or -g')

        prompt = "Add usernames in %s to" % options.get('filename')
        if membership and group:
            prompt += " <%s> and <%s>?" % (membership, group)
        elif membership:
            prompt += " <%s>?" % membership
        elif group:
            prompt += " <%s>?" % group
        prompt += " [y or yes to proceed]: "

        confirmation = input(prompt).rstrip()
        if not (confirmation == 'y' or confirmation == 'yes'):
            print('Quitting')
            return

        with open(options.get('filename')) as f:
            for line in f.readlines():
                username = line.rstrip()
                user = get_user_model().objects.get(username=username)
                if membership:
                    m = Member.objects.create(membership=membership, user=user)
                    print(m)
                if group:
                    member = Member.objects.get(membership=group.membership, user=user)
                    gm = GroupMember.objects.create(group=group, member=member)
                    print(gm)