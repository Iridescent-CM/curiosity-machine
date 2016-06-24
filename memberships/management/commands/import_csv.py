from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from django.db import transaction
from django.core.files.uploadedfile import SimpleUploadedFile
from memberships.models import MemberImport
from memberships.importer import Status
from django_rq import get_worker, get_queue
from time import sleep

class Command(BaseCommand):
    """
    Command to load user csvs from the command line, simulating upload through
    the admin. This command is intended for testing purposes, not production use.
    It works with job queues in a way that may be unsafe for production.
    """

    help = 'Import members to membership from csv file for testing (not for production)'
    args = '<membership id> <file path(s)>'
    option_list = BaseCommand.option_list + (
        make_option(
            "-w", "--worker",
            action="store_true",
            dest="worker",
            default=False,
            help="Run worker in burst mode as well"
        ),
        make_option(
            "-o", "--output",
            action="store_true",
            dest="dump_output",
            default=False,
            help="Dump output file contents to STDOUT"
        ),
        make_option(
            "-t", "--transaction",
            action="store_true",
            dest="transaction",
            default=False,
            help="Run imports inside a transaction and roll back before exiting"
        ),
    )

    def handle(self, *args, **options):
        queue = get_queue()
        if options["worker"]:
            if queue.count > 0:
                raise CommandError("Queue is not empty")
                # require an empty queue so that cleanup doesn't delete pending jobs

        if not len(args) >= 2:
            raise CommandError("Provide membership id and at least one input filename")

        try:
            int(args[0])
        except:
            raise CommandError("Provide membership id as first argument")

        if options["transaction"]:
            transaction.set_autocommit(False)
        try:
            self.run(*args, **options)
        finally:
            if options["transaction"]:
                transaction.rollback()
            queue.empty()

    def run(self, *args, **options):
        membership_id = args[0]
        filenames = args[1:]

        processing = []
        for filename in filenames:
            self.stdout.write(self.style.NOTICE("Importing %s..." % filename))
            with open(filename, mode="rb") as fp:
                obj = MemberImport(input=SimpleUploadedFile(filename, fp.read()), membership_id=membership_id)
                obj.full_clean()
                obj.save()
                processing.append(obj)

        if options["worker"]:
            self.stdout.write(self.style.NOTICE("Running worker in burst mode..."))
            get_worker().work(burst=True)

        self.stdout.write(self.style.NOTICE("Polling... "), ending='')
        self.stdout._out.flush()
        while processing:
            self.stdout.write(self.style.NOTICE('.'), ending='')
            self.stdout._out.flush()
            for obj in processing:
                obj.refresh_from_db()
                if obj.status != None:
                    self.stdout.write(self.style.MIGRATE_SUCCESS("\n%s done with status %s" % (obj.input.name, Status(obj.status).name)), ending='')
                    if options["dump_output"]:
                        self.stdout.write('')
                        self.stdout.write(obj.output.read().decode('utf-8'))
                    processing.remove(obj)
            if processing:
                sleep(1)
        self.stdout.write(self.style.NOTICE("\nDone."))
