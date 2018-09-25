from django.core.management.base import BaseCommand, CommandError
from students.models import StudentProfile
from hellosign_sdk import HSClient
from django.conf import settings
from curiositymachine import signals
import time
import hellosign_sdk
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Approve all students for whom their parents have signed the consent form'

    def add_arguments(self, parser):
        # This is the cutoff time delta for searching completed signature
        # request in days.
        parser.add_argument('cutoff', type=int, nargs='?', default=60)

    def handle(self, *args, **options):
        verbose = options["verbosity"] > 1

        current_date = datetime.today() + timedelta(1)
        cutoff_date_delta = timedelta(days=options.get('cutoff', None))
        cutoff_date = current_date - cutoff_date_delta

        # Initialize HSClient using api key
        api_key = settings.HELLOSIGN_API_KEY
        client = HSClient(api_key=api_key)
        for request_attempt in range(5):
            try:
                signature_request_list = client.get_signature_request_list()
            except hellosign_sdk.utils.exception.Conflict:
                time.sleep(10) # collided with active call, wait and retry
            else:
                break
        else:
            logger.warning("Unable to approve students: collided with active call to request list")
            return
        request = client.request

        # set the page and the number of pages of signature request to the default
        # num_pages will be updated upon the first true request
        page = 1
        num_pages = 1
        # page_size is the number of signature request per page of the
        # signature_request_list. This can be anything from 1 to 100.
        page_size = 100

        while request and page <= num_pages:
            user_ids_to_approve = []
            query = ("complete:true AND " \
                     "created:{"+ str(cutoff_date.date()) + " TO " + str(current_date.date()) + "}")
            for request_attempt in range(5):
                try:
                    signature_request_list = request.get(client.SIGNATURE_REQUEST_LIST_URL,
                                                         parameters={"query": query, "page": page,
                                                                     "page_size": page_size})
                except hellosign_sdk.utils.exception.Conflict:
                    time.sleep(10)  # collided with active call, wait and retry
                else:
                    break
            else:
                logger.warning("Unable to approve students: collided with active call to request list too many times")
                return
            signature_requests = signature_request_list["signature_requests"]

            # get the actual number of pages of signature request so that
            # we loop though all of them
            list_info = signature_request_list["list_info"]
            num_pages = list_info['num_pages']

            for signature_request in signature_requests:
                metadata = signature_request["metadata"]
                if verbose:
                    self.stdout.write(self.style.NOTICE("Signature metadata: %s" % metadata))
                if metadata and metadata["template_id"] == settings.STUDENT_CONSENT_TEMPLATE_ID:
                    # check the metadata production mode
                    if ("environment_name" in metadata
                        and metadata["environment_name"] == settings.HELLOSIGN_ENVIRONMENT_NAME
                    ):
                        user_ids_to_approve.append(metadata["user_id"])

            #user_ids_to_approve now is a list containing the user_id of students who
            #have had their parents sign consent on hellosign. We will now search the
            #student profiles for these user_ids
            if verbose:
                self.stdout.write(self.style.NOTICE("IDs to approve: %s" % user_ids_to_approve))
            student_profiles = StudentProfile.objects.filter(user_id__in=user_ids_to_approve)

            ids_approved = []
            for student_profile in student_profiles:
                if not student_profile.full_access:
                    ids_approved.append(student_profile.user.id)
                    student_profile.full_access = True
                    student_profile.save(update_fields=['full_access'])
                    signals.account_activation_confirmed.send(sender=student_profile.user)

            if verbose:
                self.stdout.write(self.style.SUCCESS("IDs approved: %s" % ids_approved))
            page = page + 1
