from argparse import ArgumentParser
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from ...api import Surveymonkey
from ...jobs import update_status
import math
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
            "--human",
            action="store_true",
            dest="human",
            help="Use human-readable formatting"
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
            "--add-survey",
            action="store",
            dest="add_survey_id",
            help="Add survey to webhook"
        )
        webhooks.add_argument(
            "--remove-survey",
            action="store",
            dest="remove_survey_id",
            help="Remove survey from webhook"
        )
        webhooks.add_argument(
            "--post",
            action="store",
            dest="post",
            help="JSON data to POST for webhook creation"
        )

        update = subparsers.add_parser(
            'update',
            help='run update job',
            description="Run update job for a survey response; run or re-run update job otherwise triggered by webhook"
        )
        update.add_argument(
            "-s", "--survey-id",
            action="store",
            dest="survey_id",
            help="Survey id"
        )
        update.add_argument(
            "-r", "--response-id",
            action="store",
            dest="response_id",
            help="Survey response id to update"
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
        elif options.get('add_survey_id'):
            self.add_survey_to_webhook(**options)
        elif options.get('remove_survey_id'):
            self.remove_survey_from_webhook(**options)
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
        if options.get('human'):
            data = res.json()
            total_pages = math.floor(data['total'] / data['per_page']) + 1
            print("*** [ Page %d/%d ] ***" % (data['page'], total_pages))
            for item in data['data']:
                print("  {id}: {name}".format(**item))
        else:
            self.pp.pprint(res.json())

    def update_webhook(self, **options):
        path = "webhooks/%s" % options.get('id')
        res = self.api.patch(path, json.loads(options.get('patch')))
        self.pp.pprint(res.json())

    def add_survey_to_webhook(self, **options):
        path = "webhooks/%s" % options.get('id')
        res = self.api.get(path)
        data = res.json()

        obj_ids = data.get('object_ids', [])
        obj_ids.append(options.get('add_survey_id'))
        obj_ids = list(set(obj_ids))

        res = self.api.patch(path, { 'object_ids': obj_ids })
        self.pp.pprint(res.json())

    def remove_survey_from_webhook(self, **options):
        path = "webhooks/%s" % options.get('id')
        res = self.api.get(path)
        data = res.json()

        obj_ids = data.get('object_ids', [])
        obj_ids.remove(options.get('remove_survey_id'))

        res = self.api.patch(path, { 'object_ids': obj_ids })
        self.pp.pprint(res.json())

    def show_webhook(self, **options):
        path = "webhooks/%s" % options.get('id')
        res = self.api.get(path)
        if options.get('human'):
            data = res.json()
            print("{id}: {name}\nHits {subscription_url} on {event_type}".format(**data))
            print("Surveys:")
            for id in data['object_ids']:
                obj_res = self.api.get('surveys/%s' % id)
                obj_data = obj_res.json()
                print("  {id}: {title}".format(**obj_data))
        else:
            self.pp.pprint(res.json())

    def handle_update(self, **options):
        update_status(options.get('survey_id'), options.get('response_id'))

    def handle_curl(self, **options):
        token = settings.SURVEYMONKEY_ACCESS_TOKEN
        print(EXAMPLE_CURL % (token, self.api.url("webhooks"), token, self.api.url("webhooks")))
        
