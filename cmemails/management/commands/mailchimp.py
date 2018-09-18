import csv
import pprint
import requests
import sys
from argparse import ArgumentParser
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Count, Max

class Command(BaseCommand):
    help = 'A Mailchimp helper. See subcommand --help statements for details.'
    pp = pprint.PrettyPrinter(indent=4)
    
    def add_arguments(self, parser):
        self.parser = parser

        subparsers = parser.add_subparsers(
            title='subcommands',
            dest='subcommand',
            parser_class=ArgumentParser
        )

        lists = subparsers.add_parser(
            'lists',
            help="list mailing lists",
            description="List details about mailing lists"
        )
        lists.add_argument(
            "-p", "--page",
            action="store",
            type=int, dest="page",
            default=1,
            help="Page number to list, default: 1"
        )
        lists.add_argument(
            "--id",
            action="store",
            dest="id",
            help="List id"
        )

        members = subparsers.add_parser(
            'members',
            help="list mailing list members",
            description="List mailing list member details"
        )
        members.add_argument(
            "-l", "--list",
            action="store",
            dest="list_id",
            required=True,
            help="List id"
        )
        members.add_argument(
            "-c", "--count-only",
            action="store_true",
            dest="count_only",
            help="Only show member count"
        )

    def handle(self, *args, **options):
        if not settings.MAILCHIMP_DATA_CENTER:
            raise CommandError('MAILCHIMP_DATA_CENTER must be set')
        self.api_base_url = 'https://%s.api.mailchimp.com/3.0/' % settings.MAILCHIMP_DATA_CENTER

        if not settings.MAILCHIMP_API_KEY:
            raise CommandError('MAILCHIMP_API_KEY must be set')
        self.api_auth = requests.auth.HTTPBasicAuth('anystring', settings.MAILCHIMP_API_KEY)

        sub = options.get('subcommand')
        if not sub:
            self.parser.print_help()
        elif hasattr(self, 'handle_%s' % sub):
            getattr(self, 'handle_%s' % sub)(**options)
        else:
            raise CommandError('Unknown subcommand: %s' % sub)

    def handle_lists(self, **options):
        res = None

        if options.get("id"):
            res = requests.get(
                self.api_base_url + 'lists/%s?exclude_fields=_links' % options.get("id"),
                auth=self.api_auth
            )
        else:
            count = 40
            offset = (options.get("page") - 1) * count
            fields = "total_items,lists.name,lists.id"
            res = requests.get(
                self.api_base_url + 'lists?offset=%d&count=%d&fields=%s' % (offset, count, fields),
                auth=self.api_auth
            )

        self.pp.pprint(res.json())

    def handle_members(self, **options):

        res = requests.get(
            self.api_base_url + 'lists/%s/members?fields=total_items' % options.get('list_id'),
            auth=self.api_auth
        )
        total = res.json()['total_items']
        print("%d members" % total)

        if not options.get('count_only'):
            count = 250
            offset = 0
            fields = 'members.email_address'

            writer = csv.writer(sys.stdout)
            writer.writerow(["Email address", "# users", "Most recently active"])
            while offset < total:
                res = requests.get(
                    self.api_base_url + 'lists/%s/members?offset=%d&count=%d&fields=%s' % (options.get('list_id'), offset, count, fields),
                    auth=self.api_auth
                )
                for member in res.json()['members']:
                    q = get_user_model().objects.filter(email__iexact=member['email_address']).aggregate(most_recent=Max('extra__last_active_on'), count=Count('id'))
                    writer.writerow([member['email_address'], q['count'], q['most_recent']])
                offset += count
