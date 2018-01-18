from argparse import ArgumentParser
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ...api import Surveymonkey
import json
import pprint

EXAMPLE_CURL = """
# Examples borrowed from Surveymonkey API Docs
# https://developer.surveymonkey.com/api/v3/
# curl commands passed through `python -m json.tool` for pretty printing

# list webhooks

curl \\
    -H "Authorization:bearer %s" \\
    -H "Content-Type:application/json" \\
    %s \\
| python -m json.tool

# create a webhook

curl \\
    -X POST \\
    -H "Authorization:bearer %s" \\
    -H "Content-Type:application/json" \\
    %s \\
    -d \\
    '{"name":"My Webhook", "event_type":"response_completed", "object_type":"survey", "object_ids":["1234","5678"], "subscription_url":"https://surveymonkey.com/webhook_reciever"}' \\
| python -m json.tool

"""

class Command(BaseCommand):
    help = 'A Surveymonkey helper for configuring webhooks. See subcommand --help statements for details.'
    pp = pprint.PrettyPrinter(indent=4)
    api = Surveymonkey()

    def add_arguments(self, parser):
        self.parser = parser

        subparsers = parser.add_subparsers(
            title='subcommands',
            dest='subcommand',
            parser_class=ArgumentParser
        )

        surveys = subparsers.add_parser(
            'surveys',
            help="list surveys",
            description="List details about surveys, listed by page, title search, or id lookup"
        )
        surveys.add_argument(
            "-p", "--page",
            action="store",
            dest="page",
            default=1,
            help="Page number to list, default: 1"
        )
        surveys.add_argument(
            "-t", "--title",
            action="store",
            dest="title",
            help="Survey title to search"
        )
        surveys.add_argument(
            "--id",
            action="store",
            dest="id",
            help="Webhook id"
        )

        webhooks = subparsers.add_parser(
            'webhooks',
            help='list and edit webhooks',
            description="List and edit webhooks; can be used to edit webhook urls, object ids, etc."
        )
        webhooks.add_argument(
            "-p", "--page",
            action="store",
            dest="page",
            default=1,
            help="Page number to list"
        )
        webhooks.add_argument(
            "--id",
            action="store",
            dest="id",
            help="Webhook id"
        )
        webhooks.add_argument(
            "--patch",
            action="store",
            dest="patch",
            help="JSON data to PATCH to webhook for update (requires id)"
        )
        webhooks.add_argument(
            "--post",
            action="store",
            dest="post",
            help="JSON data to POST for webhook creation"
        )

        curl = subparsers.add_parser(
            'curl',
            help='example curls statements',
            description="Example curl statements that could be used to manipulate the API. Handy for things the other commands don't let you do. Copy, paste, adjust, and run.",
        )

    def handle(self, *args, **options):
        sub = options.get('subcommand')
        if not sub:
            self.parser.print_help()
        elif hasattr(self, 'handle_%s' % sub):
            getattr(self, 'handle_%s' % sub)(**options)
        else:
            raise CommandError('Unknown subcommand: %s' % sub)

    def handle_surveys(self, **options):
        res = None

        if options.get("id"):
            res = self.api.get('surveys/%s' % options.get("id"))
        else:
            payload = {
                "page": options.get("page")
            }
            if options.get("title"):
                payload["title"] = options.get("title")

            res = self.api.get('surveys', payload)

        self.pp.pprint(res.json())

    def handle_webhooks(self, **options):
        if options.get('post'):
            self.create_webhook(**options)
        elif not options.get('id'):
            self.list_webhooks(**options)
        elif options.get('patch'):
            self.update_webhook(**options)
        else:
            self.show_webhook(**options)

    def create_webhook(self, **options):
        path = "webhooks"
        res = self.api.post(path, json.loads(options.get('post')))
        self.pp.pprint(res.json())

    def list_webhooks(self, **options):
        path = "webhooks"
        payload = {
            "page": options.get("page")
        }
        res = self.api.get(path, payload)
        self.pp.pprint(res.json())

    def update_webhook(self, **options):
        path = "webhooks/%s" % options.get('id')
        res = self.api.patch(path, json.loads(options.get('patch')))
        self.pp.pprint(res.json())

    def show_webhook(self, **options):
        path = "webhooks/%s" % options.get('id')
        res = self.api.get(path)
        self.pp.pprint(res.json())

    def handle_curl(self, **options):
        token = settings.SURVEYMONKEY_ACCESS_TOKEN
        print(EXAMPLE_CURL % (token, self.api.url("webhooks"), token, self.api.url("webhooks")))
        
