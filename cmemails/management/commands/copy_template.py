from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import mandrill
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Copy Mandrill template'

    def add_arguments(self, parser):
        parser.add_argument("source", metavar="<source name>")
        parser.add_argument("target", metavar="<target name>", nargs="?")
        parser.add_argument(
            "-d", "--draft",
            action="store_false",
            dest="publish",
            default=True,
            help="Make target template a draft instead of publishing"
        )
        parser.add_argument(
            "-p", "--prefix",
            action="store",
            dest="prefix",
            help="Ignore <target name>, if provided, and use <prefix + source name> as target"
        )

    def handle(self, *args, **options):
        if not ((options["source"] and options["target"])
            or (options["source"] and options["prefix"])
        ):
            raise CommandError('Provide source and target template names')

        source_name = options["source"]

        if options["prefix"]:
            target_name = options["prefix"] + source_name
        else:
            target_name = options["target"]

        mandrill_client = mandrill.Mandrill(settings.MANDRILL_API_KEY)
        try:
            source_info = mandrill_client.templates.info(name=source_name)
        except mandrill.UnknownTemplateError:
            raise CommandError('No template named %s through Mandrill API key %s' % (source_name, settings.MANDRILL_API_KEY))

        copy_info = {
            "from_email": source_info['publish_from_email'],
            "from_name": source_info['publish_from_name'],
            "subject": source_info['publish_subject'],
            "code": source_info['publish_code'],
            "text": source_info['publish_text'],
            "publish": options["publish"],
            "labels": source_info['labels']
        }
        # source values equal to None should become '' when setting the target, as None is considered "no change"
        copy_info = {k: v or '' for k, v in copy_info.items()}

        try:
            mandrill_client.templates.update(name=target_name, **copy_info)
            logger.info('Updated %s' % (target_name))
        except mandrill.UnknownTemplateError:
            mandrill_client.templates.add(name=target_name, **copy_info)
            logger.info('Added %s' % (target_name))

