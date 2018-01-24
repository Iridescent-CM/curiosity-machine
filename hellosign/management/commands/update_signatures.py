from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from ...api import HelloSign
from ...models import *

class Command(BaseCommand):
    help = "Updates the status of Hellosign Signatures"

    def add_arguments(self, parser):
        parser.add_argument(
            '-c', '--cutoff',
            action="store",
            type=int,
            dest="cutoff",
            default=60,
            help="Cutoff in 'days ago', older will not be updated"
        )
        parser.add_argument(
            '-t', '--template',
            action="append",
            dest="template_ids",
            default=[],
            help="Template ids to process signatures for"
        ) # For now, explicitly name templates. Later, processing all by default may be nicer.

    def handle(self, *args, **options):
        if not options['template_ids']:
            raise CommandError("No template ids specified")
        verbose = options.get('verbosity') > 1

        current_date = datetime.today() + timedelta(1)
        cutoff_date = current_date - timedelta(days=options.get('cutoff'))

        api = HelloSign()
        for i, page in enumerate(api.completed_signature_requests(cutoff_date.date(), current_date.date())):
            if verbose:
                self.stdout.write(self.style.NOTICE("Processing page %d, %d signatures" % (i+1, len(page))))
            approved = []
            for signature in page:
                metadata = signature.get("metadata", {})
                if metadata.get("template_id") in options['template_ids']:
                    sig_id = metadata['signature_id']
                    if verbose:
                        self.stdout.write(self.style.SUCCESS("%s signed" % sig_id))
                    approved.append(sig_id)

        Signature.objects.filter(id__in=approved).update(status=SignatureStatus.SIGNED)
        if verbose:
            self.stdout.write(self.style.SUCCESS("Done."))
