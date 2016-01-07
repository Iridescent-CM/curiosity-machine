from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from optparse import make_option
import mandrill

class Command(BaseCommand):
    help = 'Copy Mandrill template'
    args = '<source name> <target name>'
    option_list = BaseCommand.option_list + (
        make_option(
            "-p", "--publish",
            action="store_true",
            dest="publish",
            default=False,
            help="Publish target template, instead of saving changes as draft"
        ),
        make_option(
            "-x", "--prefix",
            action="store",
            dest="prefix",
            help="Ignore <target name>, if provided, and use <prefix + source name> as target"
        )
    )

    def handle(self, *args, **options):
        if not ((options["prefix"] and len(args) >= 1) or len(args) == 2):
            raise CommandError('Provide source and target template names')

        source_name = args[0]

        if options["prefix"]:
            target_name = options["prefix"] + source_name
        else:
            target_name = args[1]

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
        except mandrill.UnknownTemplateError:
            mandrill_client.templates.add(name=target_name, **copy_info)

