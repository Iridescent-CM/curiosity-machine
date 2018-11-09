from argparse import ArgumentParser
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from families.awardforce import Api
import pprint
import requests

class Command(BaseCommand):
    help = 'An AwardForce API helper. See subcommand --help statements for details.'
    pp = pprint.PrettyPrinter(indent=4)
    api = Api()

    def add_arguments(self, parser):
        self.parser = parser

        subparsers = parser.add_subparsers(
            title='subcommands',
            dest='subcommand',
            parser_class=ArgumentParser
        )

        users = subparsers.add_parser(
            'users',
            help="Interact with users API",
            description="Interact with users API",
        )
        users.add_argument(
            "-e", "--email",
            action="store",
            dest="email",
            required=True,
            help="User email"
        )
        users.add_argument(
            "-f", "--first-name",
            action="store",
            dest="first",
            required=True,
            help="User first name"
        )
        users.add_argument(
            "-l", "--last-name",
            action="store",
            dest="last",
            required=True,
            help="User last name"
        )

        token = subparsers.add_parser(
            'token',
            help="Generate an Access Token",
            description="Generate an Access Token to use in settings.py"
        )

    def handle(self, *args, **options):
        sub = options.get('subcommand')
        if not sub:
            self.parser.print_help()
        elif hasattr(self, 'handle_%s' % sub):
            getattr(self, 'handle_%s' % sub)(**options)
        else:
            raise CommandError('Unknown subcommand: %s' % sub)

    def handle_users(self, **options):
        slug = self.api.create_user(
            email=options.get('email'),
            first_name=options.get('first'),
            last_name=options.get('last')
        )
        print("Slug: %s" % slug)

        authtoken = self.api.get_auth_token(slug)
        if authtoken:
            print('Login URL: %s' % self.api.get_login_url(authtoken))

    def handle_token(self, **options):
        print("Access token: %s" % self.api.get_new_access_token())
        print("Set this token in your environment as AWARDFORCE_ACCESS_TOKEN if you don't already have one")