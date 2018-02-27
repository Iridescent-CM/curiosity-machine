from datetime import datetime, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from ...api import HelloSign
from ...models import *
from ...updating import Updating
import pprint

class Command(BaseCommand):
    help = "Updates the status of Hellosign Signatures"
    pp = pprint.PrettyPrinter(indent=4)

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
        debug = options.get('verbosity') > 2

        current_date = datetime.today() + timedelta(1)
        cutoff_date = current_date - timedelta(days=options.get('cutoff'))

        api = HelloSign()
        approved = []
        if verbose:
            self.stdout.write(self.style.NOTICE("Searching from %s to %s" % (cutoff_date.date(), current_date.date())))
        for i, page in enumerate(api.completed_signature_requests(cutoff_date.date(), current_date.date())):
            if debug:
                self.stdout.write(self.style.NOTICE("Processing page %d, %d signatures" % (i+1, len(page))))
            for signature in page:
                if debug:
                    self.pp.pprint(signature)
                metadata = signature.get("metadata", {})
                if metadata.get("template_id") in options['template_ids']:
                    sig_id = metadata['signature_id']
                    if debug:
                        self.stdout.write(self.style.SUCCESS("%s signed" % sig_id))
                    approved.append(sig_id)

        for signature in Signature.objects.filter(~Q(status=SignatureStatus.SIGNED)).filter(id__in=approved).all():
            if verbose:
                self.stdout.write(self.style.SUCCESS("Updating %s -> SIGNED" % signature.id))
            Updating(signature, SignatureStatus.SIGNED).run()
        if verbose:
            self.stdout.write(self.style.SUCCESS("Done."))
