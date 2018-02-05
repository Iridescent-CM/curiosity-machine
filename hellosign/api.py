from django.conf import settings
from hellosign_sdk import HSClient
import hellosign_sdk
import logging
import time

logger = logging.getLogger(__name__)

RETRIES = 5
SLEEP = 10

class HelloSign():
    def __init__(self, *args, **kwargs):
        self.client = HSClient(api_key=settings.HELLOSIGN_API_KEY)

    def request_signature(self, signature):
        self.client.send_signature_request_with_template(
            test_mode=not settings.HELLOSIGN_PRODUCTION_MODE,
            template_id=signature.template_id,
            custom_fields=signature.get_custom_fields(),
            signers=signature.get_signers(),
            subject=signature.get_subject(),
            message=signature.get_message(),
            metadata=signature.get_metadata(),
        )

    def get_signature_request_list(self, query, page=1, page_size=100):
        for attempt in range(RETRIES):
            try:
                # the sdk get_signature_request_list method takes no query parameters, bypass it a bit
                return self.client._get_request().get(
                    self.client.SIGNATURE_REQUEST_LIST_URL,
                    parameters={
                        "query": query,
                        "page": page,
                        "page_size": page_size,
                    }
                )
            except hellosign_sdk.utils.exception.Conflict:
                logger.warning("API request attempt %d failed:" % attempt, exc_info=True)
                time.sleep(SLEEP)  # collided with active call, wait and retry
        else:
            raise hellosign_sdk.utils.exception.Conflict("API conflict encountered on %d retries" % RETRIES)

    def completed_signature_requests(self, cutoff_date, current_date, page_size=100):
        query = "complete:true AND created:{%s TO %s}" % (
            cutoff_date,
            current_date
        )
        page = 1
        num_pages = 1
        while page <= num_pages:
            signature_request_list = self.get_signature_request_list(
                query=query,
                page=page,
                page_size=page_size,
            )
            num_pages = signature_request_list["list_info"]["num_pages"]
            yield signature_request_list["signature_requests"]
            page += 1
