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
    help = 'Approve all underage users for whom their parents have signed the consent form'

    def add_arguments(self, parser):
        # This is the cutoff time delta for searching completed signature
        # request in days.
        parser.add_argument('cutoff', type=int, nargs='?', default=60)

    def handle(self, *args, **options):

        current_date = datetime.today() + timedelta(1)
        cutoff_date_delta = timedelta(days=options.get('cutoff', None))
        cutoff_date = current_date - cutoff_date_delta
        if settings.HELLOSIGN_PRODUCTION_MODE:
            test_mode = False
        else:
            test_mode = True

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
            logger.warning("Unable to approve underage students: collided with active call to request list")
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
                     "test_mode:"+ str(test_mode)+ " AND " \
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
                logger.warning("Unable to approve underage students: collided with active call to request list too many times")
                return
            signature_requests = signature_request_list["signature_requests"]

            # get the actual number of pages of signature request so that
            # we loop though all of them
            list_info = signature_request_list["list_info"]
            num_pages = list_info['num_pages']

            # we need to check the metadata of each signature request to see if it meets
            # the following condition(s):
            # 1) it must have the current UNDERAGE_CONSENT_TEMPLATE_ID as defined in
            #   the settings. This allows us to have other hellosign templates sent out
            #   without confusing them with the underage form.
            # 2) The production mode in the signature_request metadata must match the
            #	production mode of the deployed server.
            # if the metadata meets the former condition(s), then it should contain
            # a user_id; add it to the list so that we can approve this user.
            for signature_request in signature_requests:
                metadata = signature_request["metadata"]
                if metadata and metadata["template_id"] == settings.UNDERAGE_CONSENT_TEMPLATE_ID:
                    # check the metadata production mode
                    if "production_mode" in metadata and metadata["production_mode"] == "True":
                        metadata_production_mode = True
                    else:
                        metadata_production_mode = False
                    if metadata_production_mode == settings.HELLOSIGN_PRODUCTION_MODE:
                        user_ids_to_approve.append(metadata["user_id"])

            #user_ids_to_approve now is a list containing the user_id of students who
            #have had their parents sign consent on hellosign. We will now search the
            #student profiles for these user_ids
            student_profiles = StudentProfile.objects.filter(user_id__in=user_ids_to_approve)

            #now "student_profiles" contains all the student_profiles which have completed a
            #underage consent form. Approve them if they are not already approved.
            for student_profile in student_profiles:
                if not student_profile.user.extra.approved and student_profile.birthday and student_profile.is_underage():
                    student_profile.user.extra.approved = True
                    student_profile.user.extra.save(update_fields=['approved'])
                    signals.underage_activation_confirmed.send(sender=student_profile.user,
                                                               account=student_profile.user)
            page = page + 1